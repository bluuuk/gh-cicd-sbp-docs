import argparse
import json
import logging
import os
import time
import uuid
from collections import defaultdict
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from google import genai
from google.cloud import storage
from pydantic import BaseModel

# --- Constants & Configuration ---
MODEL_ID = "gemini-3.1-pro-preview"
LOCATION = "us-central1"
DEFAULT_PROJECT_ID = "gh-docs-no-org"

load_dotenv()
load_dotenv(".secret")

parser = argparse.ArgumentParser(description="Map extracted security advice to OWASP CI/CD units.")
parser.add_argument(
    "-s",
    "--stage",
    default="test",
    help="Stage to run (default: test)",
)
parser.add_argument(
    "-e",
    "--experiment",
    required=True,
    help="Experiment name (required)",
)
parser.add_argument(
    "--project-id",
    default=os.getenv("PROJECT_ID", DEFAULT_PROJECT_ID),
    help=f"GCP project id (default: env PROJECT_ID or {DEFAULT_PROJECT_ID})",
)
parser.add_argument(
    "--gcs-bucket",
    default=os.getenv("GCS_BUCKET"),
    help="Existing GCS bucket name. If omitted, a random bucket name is generated and created automatically.",
)
parser.add_argument(
    "--credentials-file",
    default=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
    help="Path to a GCP service account JSON file. Defaults to env GOOGLE_APPLICATION_CREDENTIALS.",
)
args = parser.parse_args()

STAGE = args.stage
EXPERIMENT = args.experiment
PROJECT_ID = args.project_id
GCS_BUCKET = args.gcs_bucket
CREDENTIALS_FILE = args.credentials_file

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    style="{",
    format="{asctime} - {levelname} - {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
)

if not EXPERIMENT or not PROJECT_ID:
    logger.error("Missing required configuration: EXPERIMENT or PROJECT_ID.")
    raise SystemExit(1)

if CREDENTIALS_FILE:
    credentials_path = Path(CREDENTIALS_FILE).expanduser()
    if not credentials_path.exists():
        logger.error(f"Credentials file not found: {credentials_path}")
        raise SystemExit(1)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(credentials_path)
    logger.info(f"Using credentials file: {credentials_path}")
else:
    logger.warning(
        "No credentials file configured. Set GOOGLE_APPLICATION_CREDENTIALS or pass --credentials-file."
    )


def resolve_experiment_path(experiment: str) -> Path:
    version_path = Path.cwd() / "experiments" / experiment
    if version_path.exists():
        return version_path

    version_path = Path(__file__).parent / "experiments" / experiment
    if version_path.exists():
        return version_path

    logger.error(f"Experiment path not found for experiment '{experiment}'.")
    raise SystemExit(1)


def resolve_owasp_path() -> Path:
    owasp_path = Path(__file__).parent / "resources" / "owasp-top-10-cicd-units-topic.md"
    if owasp_path.exists():
        return owasp_path

    owasp_path = Path.cwd() / "resources" / "owasp-top-10-cicd-units-topic.md"
    if owasp_path.exists():
        return owasp_path

    logger.error("OWASP topics file not found.")
    raise SystemExit(1)


def generate_bucket_name(project_id: str) -> str:
    suffix = uuid.uuid4().hex[:12]
    return f"{project_id}-owasp-{suffix}".lower()


def ensure_bucket(storage_client: storage.Client, bucket_name: str) -> storage.Bucket:
    bucket = storage_client.lookup_bucket(bucket_name)
    if bucket is not None:
        logger.info(f"Using existing bucket: {bucket_name}")
        return bucket

    bucket = storage.Bucket(storage_client, name=bucket_name)
    bucket.storage_class = "STANDARD"
    bucket = storage_client.create_bucket(bucket, location=LOCATION)
    logger.info(f"Created bucket: {bucket.name} in {LOCATION}")
    return bucket


version_path = resolve_experiment_path(EXPERIMENT)
owasp_path = resolve_owasp_path()
owasp_units = owasp_path.read_text()

SYSTEM_PROMPT = f"""You are a security expert. You will be given a 'security-advice' extraction from a document.
Your task is to map this advice to zero or more items from the following OWASP Top 10 CI/CD units.

OWASP CI/CD TOP 10 Units:
{owasp_units}

Instructions:
- Analyze the security advice.
- Identify all relevant OWASP units that this advice relates to.
- Return the list of OWASP unit IDs (e.g., ["OWASP/1.1.1", "OWASP/9.1.1"]).
- If no units are relevant, return an empty list [].
"""


class OWASPClassification(BaseModel):
    owasp_units: List[str]


input_path = version_path / "outputs" / f"result-{STAGE}.jsonl"
output_path = version_path / "outputs" / f"owasp-{STAGE}.jsonl"
grouped_output_path = version_path / "outputs" / f"owasp-grouped-{STAGE}.json"

if not input_path.exists():
    logger.error(f"Input file not found: {input_path}")
    raise SystemExit(1)

advices_to_process = []
with input_path.open() as f:
    for line in f:
        if not line.strip():
            continue
        data = json.loads(line)
        doc_id = data.get("document_id")
        for ext in data.get("extractions", []):
            if ext.get("extraction_class") == "security_advice":
                advices_to_process.append(
                    {
                        "document_id": doc_id,
                        "extraction_text": ext.get("extraction_text"),
                    }
                )

if not advices_to_process:
    logger.info(f"No security advice items found in {input_path}")
    raise SystemExit(0)

logger.info(f"Preparing Vertex AI Batch job for {len(advices_to_process)} items using {MODEL_ID}")

batch_input_path = version_path / "outputs" / f"batch_input_{STAGE}.jsonl"
with batch_input_path.open("w") as f:
    for i, item in enumerate(advices_to_process):
        prompt = f"Security advice: {item['extraction_text']}"
        request = {
            "contents": [
                {
                    "parts": [{"text": prompt}],
                    "role": "user",
                }
                ],
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "generation_config": {
                "temperature": 0.0,
                "response_mime_type": "application/json",
                "response_schema": OWASPClassification.model_json_schema(),
            },
        }
        f.write(json.dumps({"request": request, "custom_id": str(i)}) + "\n")


client = genai.Client(vertexai=True, project=PROJECT_ID,api_key=None)

storage_client = storage.Client(project=PROJECT_ID)
if not GCS_BUCKET:
    GCS_BUCKET = generate_bucket_name(PROJECT_ID)
    logger.info(f"No bucket provided. Generated bucket name: {GCS_BUCKET}")

bucket = ensure_bucket(storage_client, GCS_BUCKET)

timestamp = int(time.time())
gcs_input_uri = f"gs://{bucket.name}/batch_inputs/owasp_{STAGE}_{timestamp}.jsonl"
blob = bucket.blob(gcs_input_uri.replace(f"gs://{bucket.name}/", ""))
blob.upload_from_filename(str(batch_input_path))
logger.info(f"Uploaded input to {gcs_input_uri}")

output_uri_prefix = f"gs://{bucket.name}/batch_outputs/owasp_{STAGE}_{timestamp}/"

batch_job = client.batches.create(
    model=MODEL_ID,
    src=gcs_input_uri,
    config={"dest": output_uri_prefix},
)
logger.info(f"Vertex AI Batch job created: {batch_job.name}. Current state: {batch_job.state}")

while batch_job.state != genai.types.JobState.JOB_STATE_SUCCEEDED:
    logger.info(f"Job state: {batch_job.state}. Waiting 30 seconds...")
    time.sleep(30)
    batch_job = client.batches.get(name=batch_job.name)


logger.info("Batch job succeeded! Downloading results...")
results_map = {}
prefix = output_uri_prefix.replace(f"gs://{bucket.name}/", "")
blobs = storage_client.list_blobs(bucket.name, prefix=prefix)

found_results = False
for result_blob in blobs:
    if result_blob.name.endswith(".jsonl") and "prediction" in result_blob.name:
        logger.info(f"Downloading result file: {result_blob.name}")
        content = result_blob.download_as_text()
        for line in content.splitlines():
            if not line.strip():
                continue
            result_data = json.loads(line)
            custom_id = result_data.get("custom_id")
            if custom_id is None:
                continue

            response = result_data.get("response")
            if not response or "candidates" not in response:
                continue

            candidate = response["candidates"][0]
            if "content" not in candidate or "parts" not in candidate["content"]:
                continue

            text = candidate["content"]["parts"][0].get("text", "{}")
            try:
                classification = json.loads(text)
                results_map[int(custom_id)] = classification.get("owasp_units", [])
            except Exception as exc:
                logger.error(f"Failed to parse model response for item {custom_id}: {exc}")
        found_results = True

if not found_results:
    logger.error(f"No result files found in {output_uri_prefix}")
    raise SystemExit(1)

# Final correlation and save
final_output = []
grouped_output = defaultdict(list)
for i, item in enumerate(advices_to_process):
    classified_units = results_map.get(i, [])
    final_item = {
        "document_id": item["document_id"],
        "extraction_text": item["extraction_text"],
        "owasp_classification": classified_units,
    }
    final_output.append(final_item)

    for unit in classified_units:
        grouped_output[unit].append(
            {
                "document_id": item["document_id"],
                "extraction_text": item["extraction_text"],
            }
        )

output_path.parent.mkdir(parents=True, exist_ok=True)
with output_path.open("w") as f:
    for item in final_output:
        f.write(json.dumps(item) + "\n")

with grouped_output_path.open("w") as f:
    json.dump(dict(sorted(grouped_output.items())), f, indent=2)
    f.write("\n")

logger.info(f"Successfully processed {len(final_output)} items and saved to {output_path}")
logger.info(f"Saved grouped OWASP output to {grouped_output_path}")

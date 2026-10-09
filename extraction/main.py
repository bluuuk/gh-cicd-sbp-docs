import os
from collections.abc import Iterator
from pathlib import Path
from typing import List
import logging
import sys 
import langextract as lx
import langextract.core.data as lxdata
import yaml
from dotenv import load_dotenv
import argparse

parser = argparse.ArgumentParser(description="Tool CLI")

# --stage / -s (default: test)
parser.add_argument(
    "-s", "--stage",
    default="test",
    help="Stage to run (default: test)"
)

# --experiment / -e (required)
parser.add_argument(
    "-e", "--experiment",
    required=True,
    help="Experiment name (required)"
)

parser.add_argument(
    "-seed", "--seed",
    default=42,
    type=int,
    help="Gemini seed value"
)

# --repository / -r (default: gh-docs-2026-02-19)
parser.add_argument(
    "-r", "--repository",
    default="gh-docs-2026-02-19",
    help="Repository name (default: gh-docs-2026-02-19)"
)

parser.add_argument(
    "--cwd",
    default=Path.cwd(),
    help="Repository name (default: gh-docs-2026-02-19)"
)

args = parser.parse_args()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    style='{',
    format='{asctime} - {levelname} - {message}',
    datefmt='%Y-%m-%d %H:%M:%S'
)


if args.cwd:
    cwd = Path(args.cwd)
else:
    cwd = Path.cwd()

load_dotenv(cwd / ".secrets")
repo_path = cwd / args.repository / "content"
if not repo_path.exists():
    raise FileNotFoundError(f"{repo_path}")

version_path = cwd / "experiments" / args.experiment
if not version_path.exists():
    raise FileNotFoundError(f"{version_path}")

config_path = version_path / "config.yaml"
if not config_path.exists():
    raise FileNotFoundError(f"{config_path}")

config = yaml.safe_load(config_path.read_text())

logger.info(f"Using repo={repo_path}")
logger.info(f"Using version={version_path}")

prompt = (version_path / "prompt").read_text()

logger.debug(f"Using {prompt=}")

stage = args.stage.lower()
input_files: Iterator[Path] = None

if (version_path / f"{stage}.files").exists():
    with (version_path / f"{stage}.files").open() as f:
        input_files = [(repo_path / file.strip()) for file in f.read().splitlines()]
else:
    raise ValueError(f"No dataset found for {stage}.files")

if stage == "all":
    logger.debug(f"<--- Production mode --->")
else:
    logger.debug(f"Using {len(input_files)} files")

raw_data = []
examples = config.get("EXAMPLES","training.yaml")
if not (version_path / examples).is_file():
    raise ValueError(f"No few shot examples found for {examples}")
raw_data = yaml.safe_load((version_path / examples).read_text())

if not raw_data:
    raw_data = dict()

logger.debug(f"Using examples: {raw_data}")

few_shots: List[lx.data.ExampleData] = []
for file,items in raw_data.items():
    extractions = []
    for extraction in items["extractions"]:
        extractions.append(
            lx.data.Extraction(
                extraction_class=extraction["extraction_class"],
                extraction_text=extraction["extraction_text"],
                attributes={} if config.get("IGNORE_ATTRIBUTES",False) else extraction["attributes"]
            )
        )
    few_shots.append(
        lx.data.ExampleData(
            text=(repo_path / file).read_text(),
            extractions=extractions
        )
    )
logger.info(f"Added {len(few_shots)} examples with{'out' if config.get('IGNORE_ATTRIBUTES',False) else ''} attributes")

base_output_path = version_path / "outputs"
base_output_path.mkdir(exist_ok=True)

all_documents = []
for file in input_files:
    all_documents.append(
        lxdata.Document(
            text=(file).read_text(),
            document_id=file.relative_to(repo_path).as_posix()
        )
    )


batching = config["BATCHING"]
logger.info(f"Batching status {batching}")

lang_model = {
    'vertexai': True,
    'project': 'gh-docs-no-org-496322',
    'location': 'global',  # South Carolina would be us-east1; needed for strorage
    'seed' : args.seed,
    # https://github.com/google/langextract/blob/main/docs/examples/batch_api_example.md
    "batch": {
        "enabled": True,
        "threshold": 1,
        "poll_interval": 15,
        "timeout": 3600 * 10,
        # Set to True to cache results in GCS. Add timestamp to prompt to force re-run.
        "enable_caching": False,
        # Retention policy for GCS bucket (days). None for permanent.
        "retention_days": 1,
    },
}

if not batching:
    del lang_model["batch"]
    
if "THINKING" in config:
    lang_model["thinking_config"] = {"thinking_level": config["THINKING"]}

def formatQA(question,answer):
    result = "\n".join([
        "Q:",
        "<<<md",
        f"{question}",
        ">>>",
        "",
        "A:",
    ])
    if answer:
        result += f"\n{answer}"
    return result + "\n"
    
# def format_example_as_text(self, example: data.ExampleData) -> str:
# """Formats a single example for the prompt.

# Args:
#     example: The example data to format.

# Returns:
#     A string representation of the example, including the question and answer.
# """
# question = example.text
# answer = self.format_handler.format_extraction_example(example.extractions)

# return "\n".join([
#     f"{self.question_prefix}{question}",
#     f"{self.answer_prefix}{answer}\n",
# ])

def patched_format_example_as_text(self, example):
    """Formats a single example for the prompt. Enhanced for markdown

    Args:
      example: The example data to format.

    Returns:
      A string representation of the example, including the question and answer.
    """
    question = example.text
    answer = self.format_handler.format_extraction_example(
        example.extractions
    )

    return formatQA(question,answer)

lx.prompting.QAPromptGenerator.format_example_as_text = patched_format_example_as_text

#   def render(self, question: str, additional_context: str | None = None) -> str:
#     """Generate a text representation of the prompt.

#     Args:
#       question: That will be presented to the model.
#       additional_context: Additional context to include in the prompt. An empty
#         string is ignored.

#     Returns:
#       Text prompt with a question to be presented to a language model.
#     """
#     prompt_lines: list[str] = [f"{self.template.description}\n"]

#     if additional_context:
#       prompt_lines.append(f"{additional_context}\n")

#     if self.template.examples:
#       prompt_lines.append(self.examples_heading)
#       for ex in self.template.examples:
#         prompt_lines.append(self.format_example_as_text(ex))

#     prompt_lines.append(f"{self.question_prefix}{question}")
#     prompt_lines.append(self.answer_prefix)
#     return "\n".join(prompt_lines)

def patched_render(self, question: str, additional_context: str | None = None) -> str:
    """Generate a text representation of the prompt.

    Args:
        question: That will be presented to the model.
        additional_context: Additional context to include in the prompt. An empty
        string is ignored.

    Returns:
        Text prompt with a question to be presented to a language model.
    """
    prompt_lines: list[str] = [f"{self.template.description}\n"]

    if additional_context:
        prompt_lines.append(f"{additional_context}\n")

    if self.template.examples:
        # prompt_lines.append(self.examples_heading)
        for ex in self.template.examples:
            prompt_lines.append(self.format_example_as_text(ex))

    prompt_lines.append(formatQA(question,None))
    return "\n".join(prompt_lines)

lx.prompting.QAPromptGenerator.render = patched_render

result = lx.extract(
    text_or_documents=all_documents,
    prompt_description=prompt,
    examples=few_shots,
    # (Maximum input tokens: 1,048,576 and Maximum output tokens: 65,535 (default))
    model_id=config.get("MODEL_ID","gemini-2.5-flash-lite"),
    # Improves recall through multiple passes
    extraction_passes=int(config.get("EXTRACTION_PASSES",1)),
    # Parallel processing for speed (batching, TBD)
    max_workers=int(config.get("MAX_WORKERS",1)),
    # batching size, gcp support up to `200,000` with 1GB input size
    batch_length=int(config.get("BATCH_LENGTH",10)),
    # Smaller contexts for better accuracy;
    max_char_buffer=int(config.get("CONTENT_LENGTH")),
    
    # Skip chunks where LLM returns malformed JSON
    resolver_params={
        "suppress_parse_errors": True,
        "accept_match_lesser" : False
    },
    # Set GOOGLE_APPLICATION_CREDENTIALS which points to the cred file
    language_model_params=lang_model,
)

results = result if isinstance(result, list) else [result]

for result in results:
    print(
f"""Task {result.document_id}      
    Extractions:
    {'\n'.join(map(repr,result.extractions))}    
""")

# Save the results to a JSONL file
lx.io.save_annotated_documents(
    results, output_name=f"result-{stage}.jsonl", output_dir=base_output_path
)

"""
https://github.com/rapidfuzz/RapidFuzz 
Before implementing more, I would love to define how to measure things!
"""
# github-cicd-sbp-and-docs

Artifact repository for the paper **_Evaluating CI/CD Security Best Practices in the GitHub Actions Documentation_**.

The project measures how well the official GitHub documentation covers CI/CD security
best practices. It does so by (1) extracting pieces of *security advice* from the GitHub
docs with an LLM, (2) mapping each piece of advice to the
[OWASP Top 10 CI/CD Security Risks](https://owasp.org/www-project-top-10-ci-cd-security-risks/),
and (3) analysing the coverage, the documentation's alert/callout usage, and comparing the
results against a manually corrected ground truth.

## Pipeline at a glance

```
GitHub docs snapshot (gh-docs-2026-02-19)
        │
        ▼
  extraction/main.py            → security_advice extractions   (result-*.jsonl)
        │
        ▼
  extraction/owasp-classify.py  → advice ⇄ OWASP CI/CD units    (owasp-*.jsonl, owasp-grouped-*.json)
        │
        ▼
  extraction/evaluate.py +      → precision / recall vs. the
  notebooks                        manually corrected ground truth
```

In parallel, `alert_analysis/` studies the Markdown *alerts* (`> [!WARNING]`, `> [!NOTE]`, …)
used throughout the documentation.

## Repository structure

### `extraction/` — the core extraction & classification pipeline
Python project managed with [`uv`](https://docs.astral.sh/uv/) (`pyproject.toml`, `uv.lock`),
plus a TypeScript sub-project for preprocessing.

| Path | Description |
| --- | --- |
| `main.py` | Runs the extraction. Uses [LangExtract](https://github.com/google/langextract) with Gemini (via Vertex AI) to pull `security_advice` extractions from the docs. Driven by an *experiment* folder and a *stage* (`test` / `all`). |
| `owasp-classify.py` | Maps each extracted piece of advice to zero or more OWASP Top 10 CI/CD units using Gemini batch jobs; writes `owasp-*.jsonl` and `owasp-grouped-*.json`. |
| `evaluate.py`, `evaluate.ipynb`, `analyse.ipynb`, `create_statistics.ipynb` | Scoring (precision/recall, fuzzy matching) and statistics/plots. |
| `experiments/` | Every prompt-engineering iteration, grouped into `buildup/`, `recall/`, `precision/`, `fuzzy/`, `validation/`, `FINAL/`, `OLD/`, … Each experiment folder holds its `config.yaml`, `prompt`, few-shot `training.yaml`, the file lists it ran on (`test.files`, `all.files`), and its `outputs/`. |
| `prompts/` | Task specs / prompt drafts used while building the tooling. |
| `preprocessor/` | Bun + TypeScript. Parses the docs Markdown (remark) and normalises frontmatter/alerts before extraction. |
| `resources/` | Shared inputs: `gh-docs-2026-02-19.zip` (the frozen GitHub-docs snapshot), `owasp-top-10-cicd-units-topic.md` (the OWASP unit catalogue used in the classifier prompt), and the `results*.latex` tables for the paper. |
| `tests/` | Unit tests for the evaluation logic. |
| `notes/` | Working notes, the OWASP↔NIST mapping sheet, and profiling traces. |
| `.devcontainer/` | VS Code dev-container definition used to run the pipeline. |

### `alert_analysis/` — study of documentation alerts/callouts
| Path | Description |
| --- | --- |
| `analyze/` | Bun + TypeScript. Scans every `*.md` file and extracts GitHub-flavoured alerts (`caution`, `important`, `note`, `tip`, `warning`) plus word counts → `analyzed.json`. |
| `eval/` | Python (`uv`) evaluation notebook/scripts over the extracted alerts. |
| `analyzed_original.json`, `analyzed_preprocessed.json`, `analyzed_old.json` | Captured alert datasets for the raw vs. preprocessed documentation. |

### `Data/` — curated artifact dataset
The frozen outputs that back the figures and numbers in the paper (copied out of the
winning `FINAL` experiment):

- `result-all.jsonl` — the full set of security-advice extractions.
- `extractions.jsonl`, `extractions_corrected.jsonl` — raw vs. manually corrected extractions (ground truth).
- `comparison_corrected.jsonl` — model output vs. ground truth, aligned for scoring.
- `owasp-grouped-all.json`, `owasp_actionable.csv`, `github_owasp_overlap_by_id.csv` — the OWASP coverage mapping.
- `owasp-top-10-cicd-units-topic.md` — the OWASP unit catalogue.
- `sha-mentions.md`, `all.files` — supporting analyses / file inventories.
- `exploration.ipynb` — the analysis notebook that produces the `*.pdf` figures
  (`advice-location.pdf`, `content-type-stats.pdf`, `github_owasp_overlap_proportions.pdf`).

## Running the pipeline

> Requires Google Cloud credentials for Vertex AI (Gemini). Secrets are read from a local
> `.secrets` / `.env` / `.secret` file and are **not** committed. A service-account JSON
> (`gh-docs-no-org-*.json`) is expected via `GOOGLE_APPLICATION_CREDENTIALS`.

```bash
# 1. Extraction (from the extraction/ directory)
cd extraction
uv sync
unzip resources/gh-docs-2026-02-19.zip              # provides the docs snapshot
uv run main.py -e <experiment-name> -s test         # or -s all for the full corpus

# 2. Map advice → OWASP units
uv run owasp-classify.py -e <experiment-name> -s test

# 3. Evaluate / analyse
uv run evaluate.py                                   # or open the notebooks

# Preprocessor (Bun)
cd preprocessor && bun install && bun run index.ts

# Alert analysis (Bun)
cd alert_analysis/analyze && bun install && bun run index.ts
```

## License

See [LICENSE](./LICENSE).

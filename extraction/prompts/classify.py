You are tasked with implementing `extraction/owasp-classify.py`:

# Task
- You will write a script that is close to `extraction/main.py`:
    - You will be given an experiment and stage as inputs
    - You will read the extractions in `{exp}/outputs/results-{stage}.jsonl`
    - For each `security-advice` extraction, you will map the extraction to zero or more items from the `rq-owasp/owasp-top-10-cicd-units-topic.md` by using a large lang. model
    - Therefore, `rq-owasp/owasp-top-10-cicd-units-topic.md` will be part of the system prompt. For now, use a generic prompt which tells the model to emit a json array, e.g. `answer=[OWASP/1.1.1,OWASP/9.1.1]` for each query against the LLM.

## Details
- Do not read, but use load_env to read .env and .secret
- Use the google SDK AI sdk, which is already installed, to generate a query that takes ONE security advice form the extraction:
    - Implement batching
- Write outputs into the file `{exp}/outputs/owasp-{stage}.jsonl`
- Package manager I am using is `uv`.
# Prompts 

## Batch 0

```
'# SecurityAdviceExtract\n\n## Task Description\nYou are a cybersecurity documentation expert specialized in identifying and categorizing security advice within GitHub documentation files (Markdown). Your goal is to extract text segments that strictly fit the definition of "Security Advice" for a developer audience. Extract characters, emotions, and relationships in order of appearance.\n      Use exact text for extractions. Do not paraphrase or overlap entities.\n      Provide meaningful attributes for each entity to add context.\n\n\n### Definition of Security Advice\nA text segment qualifies as **security_advice_body** if it contains:\n1.  A specific security risk, vulnerability, or threat.\n2.  A sequence of actions, commands, or configuration steps to achieve an outcome that reduces or mitigates that risk.\n3.  Advice targeted at solving one specific problem.\n\n### Critical Rule: EXACT MATCH ONLY\nThe extraction library uses substring matching. You must extract the text **exactly as it appears** in the source markdown.\n- **DO NOT** fix typos.\n- **DO NOT** rephrase sentences.\n- **DO NOT** change punctuation.\n- **DO NOT** expand abbreviations.\n- **DO NOT** remove Markdown syntax (bolding, code ticks, links).\n- **DO NOT** render or remove Liquid templates (e.g., `{% data ... %}`).\n\nExamples\nQ: ## Naming your secrets\n\n>[!TIP]\n> To help ensure that {% data variables.product.prodname_dotcom %} redacts your secrets in logs correctly, avoid using structured data as the values of secrets.\n\nThe following rules apply to secret names:\n\n{% data reusables.actions.actions-secrets-and-variables-naming %}\n\n{% data reusables.codespaces.secret-precedence %} Similarly, if an organization, repository, and environment all have a secret with the same name, the environment-level secret takes precedence.\n\n## Limits for secrets\n\nYou can store up to 1,000 organization secrets, 100 repository secrets, and 100 environment secrets.\n\nA workflow created in a repository can access the following number of secrets:\n\n* All 100 repository secrets.\n* If the repository is assigned access to more than 100 organization secrets, the workflow can only use the first 100 organization secrets (sorted alphabetically by secret name).\n* All 100 environment secrets.\n\nSecrets are limited to 48 KB in size. To store larger secrets, see [AUTOTITLE](/actions/how-tos/security-for-github-actions/security-guides/using-secrets-in-github-actions#storing-large-secrets).\n\n## When {% data variables.product.prodname_actions %} reads secrets\n\nOrganization and repository secrets are read when a workflow run is queued, and environment secrets are read when a job referencing the environment starts.\n\n## Automatically redacted secrets\n\n{% data variables.product.prodname_dotcom %} automatically redacts the following sensitive information from workflow logs.\n\n> [!NOTE] If you would like other types of sensitive information to be automatically redacted, please reach out to us in our [community discussions](https://github.com/orgs/community/discussions?discussions_q=is%3Aopen+label%3AActions).\n\n* 32-byte and 64-byte Azure keys\n* Azure AD client app passwords\n* Azure Cache keys\n* Azure Container Registry keys\n* Azure Function host keys\n* Azure Search keys\n* Database connection strings\n* HTTP Bearer token headers\n* JWTs\n* NPM author tokens\n* NuGet API keys\n* v1 GitHub installation tokens\n* v2 GitHub installation tokens (`ghp`, `gho`, `ghu`, `ghs`, `ghr`)\n* v2 GitHub PATs\n\n## Security\n\nFor security best practices using secrets, see [AUTOTITLE](/actions/reference/secure-use-reference#use-secrets-for-sensitive-information).\nA: ```json\n{\n  "extractions": [\n    {\n      "security_advice": ">[!TIP]\\n> To help ensure that {% data variables.product.prodname_dotcom %} redacts your secrets in logs correctly, avoid using structured data as the values of secrets.\\n",\n      "security_advice_attributes": {\n        "type": "alert"\n      }\n    },\n    {\n      "security_advice": "For security best practices using secrets, see [AUTOTITLE](/actions/reference/secure-use-reference#use-secrets-for-sensitive-information).\\n",\n      "security_advice_attributes": {\n        "type": "linked"\n      }\n    }\n  ]\n}\n```\n\nQ: ## Understanding the risk of script injections\n\nWhen creating workflows, [custom actions](/actions/creating-actions/about-custom-actions), and [composite actions](/actions/creating-actions/creating-a-composite-action), you should always consider whether your code might execute untrusted input from attackers. This can occur when an attacker adds malicious commands and scripts to a context. When your workflow runs, those strings might be interpreted as code which is then executed on the runner.\n\nAttackers can add their own malicious content to the [`github` context](/actions/learn-github-actions/contexts#github-context), which should be treated as potentially untrusted input. These contexts typically end with `body`, `default_branch`, `email`, `head_ref`, `label`, `message`, `name`, `page_name`,`ref`, and `title`. For example: `github.event.issue.title`, or `github.event.pull_request.body`.\n\nYou should ensure that these values do not flow directly into workflows, actions, API calls, or anywhere else where they could be interpreted as executable code. By adopting the same defensive programming posture you would use for any other privileged application code, you can help security harden your use of {% data variables.product.prodname_actions %}. For information on some of the steps an attacker could take, see [AUTOTITLE](/actions/security-guides/security-hardening-for-github-actions#potential-impact-of-a-compromised-runner).\n\nIn addition, there are other less obvious sources of potentially untrusted input, such as branch names and email addresses, which can be quite flexible in terms of their permitted content. For example, `zzz";echo${IFS}"hello";#` would be a valid branch name and would be a possible attack vector for a target repository.\n\nThe following sections explain how you can help mitigate the risk of script injection.\n\n### Example of a script injection attack\n\nA script injection attack can occur directly within a workflow\'s inline script. In the following example, an action uses an expression to test the validity of a pull request title, but also adds the risk of script injection:\n\n{% raw %}\n\n```yaml\n      - name: Check PR title\n        run: |\n          title="${{ github.event.pull_request.title }}"\n          if [[ $title =~ ^octocat ]]; then\n          echo "PR title starts with \'octocat\'"\n          exit 0\n          else\n          echo "PR title did not start with \'octocat\'"\n          exit 1\n          fi\n```\n\n{% endraw %}\n\nThis example is vulnerable to script injection because the `run` command executes within a temporary shell script on the runner. Before the shell script is run, the expressions inside {% raw %}`${{ }}`{% endraw %} are evaluated and then substituted with the resulting values, which can make it vulnerable to shell command injection.\n\nTo inject commands into this workflow, the attacker could create a pull request with a title of `a"; ls $GITHUB_WORKSPACE"`:\n\n![Screenshot of the title of a pull request in edit mode. A new title has been entered in the field: a"; ls $GITHUB_WORKSPACE".](/assets/images/help/actions/example-script-injection-pr-title.png)\n\nIn this example, the `"` character is used to interrupt the {% raw %}`title="${{ github.event.pull_request.title }}"`{% endraw %} statement, allowing the `ls` command to be executed on the runner. You can see the output of the `ls` command in the log:\n\n```shell\nRun title="a"; ls $GITHUB_WORKSPACE""\nREADME.md\ncode.yml\nexample.js\n```\n\nFor best practices keeping runners secure, see [AUTOTITLE](/actions/reference/secure-use-reference#good-practices-for-mitigating-script-injection-attacks).\nA: ```json\n{\n  "extractions": [\n    {\n      "security_advice": "When creating workflows, [custom actions](/actions/creating-actions/about-custom-actions), and [composite actions](/actions/creating-actions/creating-a-composite-action), you should always consider whether your code might execute untrusted input from attackers. This can occur when an attacker adds malicious commands and scripts to a context. When your workflow runs, those strings might be interpreted as code which is then executed on the runner.\\n\\nAttackers can add their own malicious content to the [`github` context](/actions/learn-github-actions/contexts#github-context), which should be treated as potentially untrusted input. These contexts typically end with `body`, `default_branch`, `email`, `head_ref`, `label`, `message`, `name`, `page_name`,`ref`, and `title`. For example: `github.event.issue.title`, or `github.event.pull_request.body`.\\n\\nYou should ensure that these values do not flow directly into workflows, actions, API calls, or anywhere else where they could be interpreted as executable code. By adopting the same defensive programming posture you would use for any other privileged application code, you can help security harden your use of {% data variables.product.prodname_actions %}. For information on some of the steps an attacker could take, see [AUTOTITLE](/actions/security-guides/security-hardening-for-github-actions#potential-impact-of-a-compromised-runner).\\n\\nIn addition, there are other less obvious sources of potentially untrusted input, such as branch names and email addresses, which can be quite flexible in terms of their permitted content. For example, `zzz\\";echo${IFS}\\"hello\\";#` would be a valid branch name and would be a possible attack vector for a target repository.       \\n",\n      "security_advice_attributes": {\n        "type": "textual"\n      }\n    },\n    {\n      "security_advice": "For best practices keeping runners secure, see [AUTOTITLE](/actions/reference/secure-use-reference#good-practices-for-mitigating-script-injection-attacks).\\n",\n      "security_advice_attributes": {\n        "type": "linked"\n      }\n    }\n  ]\n}\n```\n\nQ: ## Requirements for self-hosted runner machines\n\nYou can use a machine as a self-hosted runner as long as it meets these requirements:\n\n* You can install and run the self-hosted runner application on the machine. See [Supported operating systems](#supported-operating-systems) and [Supported processor architectures](#supported-processor-architectures).\n* The machine can communicate with {% data variables.product.prodname_actions %}.\n* The machine has enough hardware resources for the type of workflows you plan to run. The self-hosted runner application itself only requires minimal resources.\n* If you want to run workflows that use Docker container actions or service containers, you must use a Linux machine and Docker must be installed.\n\n### Supported operating systems\n\n#### Linux\n\n* Red Hat Enterprise Linux 8 or later\n* CentOS 8 or later\n* Oracle Linux 8 or later\n* Fedora 29 or later\n* Debian 10 or later\n* Ubuntu 20.04 or later\n* Linux Mint 20 or later\n* openSUSE 15.2 or later\n* SUSE Enterprise Linux (SLES) 15 SP2 or later\n\n#### Windows\n\n* Windows 10 64-bit\n* Windows 11 64-bit\n* Windows Server 2016 64-bit\n* Windows Server 2019 64-bit\n* Windows Server 2022 64-bit\n\n#### macOS\n\n* macOS 11.0 (Big Sur) or later\n\n### Supported processor architectures\n\n* `x64` - Linux, macOS, Windows.\n* `ARM64` - Linux, macOS{% ifversion actions-windows-arm %}, Windows (currently in {% data variables.release-phases.public_preview %}){% endif %}.\n* `ARM32` - Linux.\n\n## Routing precedence for self-hosted runners\n\nWhen routing a job to a self-hosted runner, {% data variables.product.prodname_dotcom %} looks for a runner that matches the job\'s `runs-on` labels and groups:\n\n* If {% data variables.product.prodname_dotcom %} finds an online and idle runner that matches the job\'s `runs-on` labels and groups, the job is then assigned and sent to the runner.\n  * If the runner doesn\'t pick up the assigned job within 60 seconds, the job is re-queued so that a new runner can accept it.\n* If {% data variables.product.prodname_dotcom %} doesn\'t find an online and idle runner that matches the job\'s `runs-on` labels and groups, then the job will remain queued until a runner comes online.\n* If the job remains queued for more than 24 hours, the job will fail.\n\n## Autoscaling\n\nYou can automatically increase or decrease the number of self-hosted runners in your environment in response to the webhook events you receive with a particular label.\n\n### Supported autoscaling solutions\n\n{% ifversion fpt or ghec %}\n\n{% data variables.product.prodname_dotcom %}-hosted runners inherently autoscale based on your needs. {% data variables.product.prodname_dotcom %}-hosted runners can be a low-maintenance and cost-effective alternative to developing or implementing autoscaling solutions. For more information, see [AUTOTITLE](/actions/using-github-hosted-runners/about-github-hosted-runners/about-github-hosted-runners).\n\n{% endif %}\n\nThe [actions/actions-runner-controller](https://github.com/actions/actions-runner-controller) (ARC) project is a Kubernetes-based runner autoscaler. {% data variables.product.prodname_dotcom %} recommends ARC if the team deploying it has expert Kubernetes knowledge and experience.\n\nFor more information, see [AUTOTITLE](/actions/hosting-your-own-runners/managing-self-hosted-runners-with-actions-runner-controller/about-actions-runner-controller) and [AUTOTITLE](/actions/hosting-your-own-runners/managing-self-hosted-runners-with-actions-runner-controller/about-support-for-actions-runner-controller).\n\n### Ephemeral runners for autoscaling\n\n{% data variables.product.prodname_dotcom %} recommends implementing autoscaling with ephemeral self-hosted runners; autoscaling with persistent self-hosted runners is not recommended. In certain cases, {% data variables.product.prodname_dotcom %} cannot guarantee that jobs are not assigned to persistent runners while they are shut down. With ephemeral runners, this can be guaranteed because {% data variables.product.prodname_dotcom %} only assigns one job to a runner.\nA: '
```

## Batch 3

```
'# SecurityAdviceExtract\n\n## Task Description\nYou are a cybersecurity documentation expert specialized in identifying and categorizing security advice within GitHub documentation files (Markdown). Your goal is to extract text segments that strictly fit the definition of "Security Advice" for a developer audience. Extract characters, emotions, and relationships in order of appearance.\n      Use exact text for extractions. Do not paraphrase or overlap entities.\n      Provide meaningful attributes for each entity to add context.\n\n\n### Definition of Security Advice\nA text segment qualifies as **security_advice_body** if it contains:\n1.  A specific security risk, vulnerability, or threat.\n2.  A sequence of actions, commands, or configuration steps to achieve an outcome that reduces or mitigates that risk.\n3.  Advice targeted at solving one specific problem.\n\n### Critical Rule: EXACT MATCH ONLY\nThe extraction library uses substring matching. You must extract the text **exactly as it appears** in the source markdown.\n- **DO NOT** fix typos.\n- **DO NOT** rephrase sentences.\n- **DO NOT** change punctuation.\n- **DO NOT** expand abbreviations.\n- **DO NOT** remove Markdown syntax (bolding, code ticks, links).\n- **DO NOT** render or remove Liquid templates (e.g., `{% data ... %}`).\n\nExamples\nQ: ## Naming your secrets\n\n>[!TIP]\n> To help ensure that {% data variables.product.prodname_dotcom %} redacts your secrets in logs correctly, avoid using structured data as the values of secrets.\n\nThe following rules apply to secret names:\n\n{% data reusables.actions.actions-secrets-and-variables-naming %}\n\n{% data reusables.codespaces.secret-precedence %} Similarly, if an organization, repository, and environment all have a secret with the same name, the environment-level secret takes precedence.\n\n## Limits for secrets\n\nYou can store up to 1,000 organization secrets, 100 repository secrets, and 100 environment secrets.\n\nA workflow created in a repository can access the following number of secrets:\n\n* All 100 repository secrets.\n* If the repository is assigned access to more than 100 organization secrets, the workflow can only use the first 100 organization secrets (sorted alphabetically by secret name).\n* All 100 environment secrets.\n\nSecrets are limited to 48 KB in size. To store larger secrets, see [AUTOTITLE](/actions/how-tos/security-for-github-actions/security-guides/using-secrets-in-github-actions#storing-large-secrets).\n\n## When {% data variables.product.prodname_actions %} reads secrets\n\nOrganization and repository secrets are read when a workflow run is queued, and environment secrets are read when a job referencing the environment starts.\n\n## Automatically redacted secrets\n\n{% data variables.product.prodname_dotcom %} automatically redacts the following sensitive information from workflow logs.\n\n> [!NOTE] If you would like other types of sensitive information to be automatically redacted, please reach out to us in our [community discussions](https://github.com/orgs/community/discussions?discussions_q=is%3Aopen+label%3AActions).\n\n* 32-byte and 64-byte Azure keys\n* Azure AD client app passwords\n* Azure Cache keys\n* Azure Container Registry keys\n* Azure Function host keys\n* Azure Search keys\n* Database connection strings\n* HTTP Bearer token headers\n* JWTs\n* NPM author tokens\n* NuGet API keys\n* v1 GitHub installation tokens\n* v2 GitHub installation tokens (`ghp`, `gho`, `ghu`, `ghs`, `ghr`)\n* v2 GitHub PATs\n\n## Security\n\nFor security best practices using secrets, see [AUTOTITLE](/actions/reference/secure-use-reference#use-secrets-for-sensitive-information).\nA: ```json\n{\n  "extractions": [\n    {\n      "security_advice": ">[!TIP]\\n> To help ensure that {% data variables.product.prodname_dotcom %} redacts your secrets in logs correctly, avoid using structured data as the values of secrets.\\n",\n      "security_advice_attributes": {\n        "type": "alert"\n      }\n    },\n    {\n      "security_advice": "For security best practices using secrets, see [AUTOTITLE](/actions/reference/secure-use-reference#use-secrets-for-sensitive-information).\\n",\n      "security_advice_attributes": {\n        "type": "linked"\n      }\n    }\n  ]\n}\n```\n\nQ: ## Understanding the risk of script injections\n\nWhen creating workflows, [custom actions](/actions/creating-actions/about-custom-actions), and [composite actions](/actions/creating-actions/creating-a-composite-action), you should always consider whether your code might execute untrusted input from attackers. This can occur when an attacker adds malicious commands and scripts to a context. When your workflow runs, those strings might be interpreted as code which is then executed on the runner.\n\nAttackers can add their own malicious content to the [`github` context](/actions/learn-github-actions/contexts#github-context), which should be treated as potentially untrusted input. These contexts typically end with `body`, `default_branch`, `email`, `head_ref`, `label`, `message`, `name`, `page_name`,`ref`, and `title`. For example: `github.event.issue.title`, or `github.event.pull_request.body`.\n\nYou should ensure that these values do not flow directly into workflows, actions, API calls, or anywhere else where they could be interpreted as executable code. By adopting the same defensive programming posture you would use for any other privileged application code, you can help security harden your use of {% data variables.product.prodname_actions %}. For information on some of the steps an attacker could take, see [AUTOTITLE](/actions/security-guides/security-hardening-for-github-actions#potential-impact-of-a-compromised-runner).\n\nIn addition, there are other less obvious sources of potentially untrusted input, such as branch names and email addresses, which can be quite flexible in terms of their permitted content. For example, `zzz";echo${IFS}"hello";#` would be a valid branch name and would be a possible attack vector for a target repository.\n\nThe following sections explain how you can help mitigate the risk of script injection.\n\n### Example of a script injection attack\n\nA script injection attack can occur directly within a workflow\'s inline script. In the following example, an action uses an expression to test the validity of a pull request title, but also adds the risk of script injection:\n\n{% raw %}\n\n```yaml\n      - name: Check PR title\n        run: |\n          title="${{ github.event.pull_request.title }}"\n          if [[ $title =~ ^octocat ]]; then\n          echo "PR title starts with \'octocat\'"\n          exit 0\n          else\n          echo "PR title did not start with \'octocat\'"\n          exit 1\n          fi\n```\n\n{% endraw %}\n\nThis example is vulnerable to script injection because the `run` command executes within a temporary shell script on the runner. Before the shell script is run, the expressions inside {% raw %}`${{ }}`{% endraw %} are evaluated and then substituted with the resulting values, which can make it vulnerable to shell command injection.\n\nTo inject commands into this workflow, the attacker could create a pull request with a title of `a"; ls $GITHUB_WORKSPACE"`:\n\n![Screenshot of the title of a pull request in edit mode. A new title has been entered in the field: a"; ls $GITHUB_WORKSPACE".](/assets/images/help/actions/example-script-injection-pr-title.png)\n\nIn this example, the `"` character is used to interrupt the {% raw %}`title="${{ github.event.pull_request.title }}"`{% endraw %} statement, allowing the `ls` command to be executed on the runner. You can see the output of the `ls` command in the log:\n\n```shell\nRun title="a"; ls $GITHUB_WORKSPACE""\nREADME.md\ncode.yml\nexample.js\n```\n\nFor best practices keeping runners secure, see [AUTOTITLE](/actions/reference/secure-use-reference#good-practices-for-mitigating-script-injection-attacks).\nA: ```json\n{\n  "extractions": [\n    {\n      "security_advice": "When creating workflows, [custom actions](/actions/creating-actions/about-custom-actions), and [composite actions](/actions/creating-actions/creating-a-composite-action), you should always consider whether your code might execute untrusted input from attackers. This can occur when an attacker adds malicious commands and scripts to a context. When your workflow runs, those strings might be interpreted as code which is then executed on the runner.\\n\\nAttackers can add their own malicious content to the [`github` context](/actions/learn-github-actions/contexts#github-context), which should be treated as potentially untrusted input. These contexts typically end with `body`, `default_branch`, `email`, `head_ref`, `label`, `message`, `name`, `page_name`,`ref`, and `title`. For example: `github.event.issue.title`, or `github.event.pull_request.body`.\\n\\nYou should ensure that these values do not flow directly into workflows, actions, API calls, or anywhere else where they could be interpreted as executable code. By adopting the same defensive programming posture you would use for any other privileged application code, you can help security harden your use of {% data variables.product.prodname_actions %}. For information on some of the steps an attacker could take, see [AUTOTITLE](/actions/security-guides/security-hardening-for-github-actions#potential-impact-of-a-compromised-runner).\\n\\nIn addition, there are other less obvious sources of potentially untrusted input, such as branch names and email addresses, which can be quite flexible in terms of their permitted content. For example, `zzz\\";echo${IFS}\\"hello\\";#` would be a valid branch name and would be a possible attack vector for a target repository.       \\n",\n      "security_advice_attributes": {\n        "type": "textual"\n      }\n    },\n    {\n      "security_advice": "For best practices keeping runners secure, see [AUTOTITLE](/actions/reference/secure-use-reference#good-practices-for-mitigating-script-injection-attacks).\\n",\n      "security_advice_attributes": {\n        "type": "linked"\n      }\n    }\n  ]\n}\n```\n\nQ: In addition, your workflow may require access to other network resources.\n\nIf you use an IP address allow list for your {% data variables.product.prodname_dotcom %} organization or enterprise account, you must add your self-hosted runner\'s IP address to the allow list. See [Managing allowed IP addresses for your organization](/{% ifversion fpt %}enterprise-cloud@latest/{% endif %}/organizations/keeping-your-organization-secure/managing-allowed-ip-addresses-for-your-organization#using-github-actions-with-an-ip-allow-list) or [Enforcing policies for security settings in your enterprise](/{% ifversion fpt %}enterprise-cloud@latest/{% endif %}admin/policies/enforcing-policies-for-your-enterprise/enforcing-policies-for-security-settings-in-your-enterprise){% ifversion fpt %} in the {% data variables.product.prodname_ghe_cloud %} documentation.{% else %}.{% endif %}\n\n{% else %}\n\n### Communication with {% data variables.product.prodname_dotcom_the_website %}\n\nSelf-hosted runners do not need to connect to {% data variables.product.prodname_dotcom_the_website %} unless you have enabled automatic access to {% data variables.product.prodname_dotcom_the_website %} actions for {% data variables.product.prodname_ghe_server %}. For more information, see [AUTOTITLE](/admin/github-actions/managing-access-to-actions-from-githubcom/about-using-actions-in-your-enterprise).\n\nIf you want your runner to connect to {% data variables.product.prodname_dotcom_the_website %}, the host machine must be able to make outbound HTTP connections over port 80, or HTTPS connections over port 443. To ensure connectivity over HTTPS, configure TLS for {% data variables.product.prodname_ghe_server %}. See [AUTOTITLE](/enterprise-server@latest/admin/configuration/hardening-security-for-your-enterprise/configuring-tls).\n\nIf you have enabled automatic access to {% data variables.product.prodname_dotcom_the_website %} actions, then the self-hosted runner will connect directly to {% data variables.product.prodname_dotcom_the_website %} to download actions. You must ensure that the machine has the appropriate network access to communicate with the {% data variables.product.prodname_dotcom %} URLs listed below.\n\n```shell copy\ngithub.com\napi.github.com\ncodeload.github.com\n```\n\nYou can use the REST API to get meta information about {% data variables.product.company_short %}, including the IP addresses and domain details for {% data variables.product.company_short %} services. The `actions_inbound` section of the API supports both fully qualified and wildcard domains. Fully qualified domains specify a complete domain name (e.g., `example.github.com`), while wildcard domains use a `*` to represent multiple possible subdomains (e.g., `*.github.com`). An example of the self-hosted runner requirements using wildcard domains has been listed below. For more information, see [AUTOTITLE](/rest/meta/meta).\n\n```shell copy\ngithub.com\n*.github.com\n*.githubusercontent.com\nghcr.io\n```\n\n{% data reusables.actions.domain-name-cname-recursive-firewall-rules %}\n\n{% endif %}\nA: '
```

# Ollama Model Reponses


```json
{
    "model": "gemma2:9b",
    "created_at": "2026-02-11T00:21:18.955654915Z",
    "response": "{\n  \"extractions\": [\n    {\n      \"security_advice\": \"The machine has enough hardware resources for the type of workflows you plan to run. The self-hosted runner application itself only requires minimal resources.\\n\",\n      \"security_advice_attributes\": {\n        \"type\": \"textual\"\n      }\n    },\n    {\n      \"security_advice\": \"If you want to run workflows that use Docker container actions or service containers, you must use a Linux machine and Docker must be installed.\\n\",\n      \"security_advice_attributes\": {\n        \"type\": \"textual\"\n      }\n    },\n    {\n      \"security_advice\": \"In certain cases, {% data variables.product.prodname_dotcom %} cannot guarantee that jobs are not assigned to persistent runners while they are shut down. With ephemeral runners, this can be guaranteed because {% data variables.product.prodname_dotcom %} only assigns one job to a runner.\\n\",\n      \"security_advice_attributes\": {\n        \"type\": \"textual\"\n      }\n    }\n  ]\n}",
    "done": true,
    "done_reason": "stop",
    "context": [
        106,
        1645,
        ...
        235270
    ],
    "total_duration": 19897845052,
    "load_duration": 181084506,
    "prompt_eval_count": 3403,
    "prompt_eval_duration": 44795389,
    "eval_count": 244,
    "eval_duration": 10948568455
}
```

The timings are in nanoseconds, I think 10^^9 -> 

```
19897845052 / pow(10,9)
19.897845052
```

So one run takes 20 seconds, 4 runs are then at 60 seconds. <https://docs.ollama.com/api/usage>

# Base calculation

```
❯ fd -g "*.md" -x basename | sort | uniq -c | sort -nr | head -n 10
 656 index.md
  84 README.md
  17 quickstart.md
   7 guides.md
   5 secrets.md
   4 orgs.md
   4 custom-properties.md
   4 comments.md
   4 best-practices.md
   4 attestations.md
```

index.md is always empty in the sense that it only contains the frontmatter (yaml)

```
❯ fd -g "*.md" -E "index.md" | wc -l
     199
❯ fd -g "*.md" -E "index.md" | shuf -n 20 > ../../../extraction/experiments/05.02/files
```

So we have 199, let's say n=200 files.

## Tokens

```
(extraction) root ➜ /workspaces/github-best-pratices/extraction (main) $ find gh-docs/content/actions/ -name "*.md" -exec wc -w {} \; | sort -nr | head -n 10
8781 gh-docs/content/actions/reference/workflows-and-actions/events-that-trigger-workflows.md
6780 gh-docs/content/actions/reference/workflows-and-actions/workflow-syntax.md
6528 gh-docs/content/actions/tutorials/use-actions-runner-controller/deploy-runner-scale-sets.md
6128 gh-docs/content/actions/reference/workflows-and-actions/contexts.md
4573 gh-docs/content/actions/reference/security/secure-use.md
4126 gh-docs/content/actions/tutorials/migrate-to-github-actions/automated-migrations/azure-devops-migration.md
3841 gh-docs/content/actions/reference/workflows-and-actions/workflow-commands.md
3763 gh-docs/content/actions/reference/security/oidc.md
3148 gh-docs/content/actions/reference/workflows-and-actions/metadata-syntax.md
3139 gh-docs/content/actions/tutorials/migrate-to-github-actions/automated-migrations/gitlab-migration.md
```

Each file is at max $9000 * 1.3 \leq 12000$ tokens. To ease calcuation, we just do it in words.
- Let $C$ be the size of one chunk
- Let $P$ be the prompt size, including examples

Therefore, we have $\dfrac{9000}{C} + P + 1.3 \cdot\dfrac{9000}{C}$ words per document. The $1.3$ is my aprox json slop factor. If we do not chunk, such that $C=1$ and our prompt size is $542 + 542 \leq 1100$, we arrive at :

$$ 1.3 \cdot (9000 + 1100 + 1.3\cdot9000) = 28340 \leq 30000$$

## Runtime

Theoretical runtime where we would have $200 * 2 * 4 = 1,600$ model invocations with less than 30k tokens. We have 4 chunked batches and 2 runs.

```
In [1]: 199 * 2 * 4 * 30
Out[1]: 47760
```

# Model selection

```
The third-generation Tensor Cores in NVIDIA A2 support integer math down to INT4 and floating-point math up to FP32 to deliver high AI training and inference performance. A2’s NVIDIA Ampere architecture also supports TF32 and NVIDIA’s automatic mixed precision (AMP) capabilities.
```

-> https://www.pny.com/en-eu/nvidia-a2

- Currently, I am working with `gemma2` which has a sequence length of 8k.
    - Uses full vRAM but can't run fp4 due to the A2 as seen above
- Need more power here if I want to do it locally

- Using gemin 2.5 flash via free vertex api credits
    - $30000 \cdot 1600 = 48.000.000$ 
        - Assuming a price of $2.5$ for every token ($2.5$ = output price $>>>$ input price $0.3$)
        - $(48.000.000 / 10^6) * 2.5 = 120$
    - Cost cat at <https://ai.google.dev/gemini-api/docs/pricing#standard_4>

# Further testing

## Output format constraints

{
    'temperature': 0.0, 'response_schema': {
        'type': 'object', 'properties': { 'extractions': { 'type': 'array', 'items': { 'type': 'object', 'properties': { 'security_advice': { 'type': 'string' }, 'security_advice_attributes': { 'type': 'object', 'properties': { 'type': { 'type': 'string' } }, 'nullable': True } } } } }, 'required': ['extractions']
    }, 'response_mime_type': 'application/json'
}

```md
# SecurityAdviceExtract

## Task Description
You are a cybersecurity documentation expert specialized in identifying and categorizing security advice within GitHub documentation files (Markdown). Your goal is to extract text segments that strictly fit the definition of "Security Advice" for a developer audience. Extract characters, emotions, and relationships in order of appearance. Use exact text for extractions. Do not paraphrase or overlap entities. Provide meaningful attributes for each entity to add context.

### Definition of Security Advice
A text segment qualifies as **security_advice_body** if it contains:
1.  A specific security risk, vulnerability, or threat.
2.  A sequence of actions, commands, or configuration steps to achieve an outcome that reduces or mitigates that risk.
3.  Advice targeted at solving one specific problem.

### Attributes
There are currently $3$ distinct single class attribute types. Assign one on the following:
- **alert** use the markdown syntax for blockquotes, e.g. `> [!Alert] \n > Do not enable debug in production`
- **linked** for security advices that point to 3rd party resources/websites
- **textual** plain written security advices

### Critical Rule: EXACT MATCH ONLY
The extraction library uses substring matching. You must extract the text **exactly as it appears** in the source markdown.
- **DO NOT** fix typos.
- **DO NOT** rephrase sentences.
- **DO NOT** change punctuation.
- **DO NOT** expand abbreviations.
- **DO NOT** remove Markdown syntax (bolding, code ticks, links).
- **DO NOT** render or remove Liquid templates (e.g., `{% data ... %}`).

Examples
Q: ## Naming your secrets

>[!TIP]
> To help ensure that {% data variables.product.prodname_dotcom %} redacts your secrets in logs correctly, avoid using structured data as the values of secrets.

The following rules apply to secret names:

{% data reusables.actions.actions-secrets-and-variables-naming %}

{% data reusables.codespaces.secret-precedence %} Similarly, if an organization, repository, and environment all have a secret with the same name, the environment-level secret takes precedence.

## Limits for secrets

You can store up to 1,000 organization secrets, 100 repository secrets, and 100 environment secrets.

A workflow created in a repository can access the following number of secrets:

* All 100 repository secrets.
* If the repository is assigned access to more than 100 organization secrets, the workflow can only use the first 100 organization secrets (sorted alphabetically by secret name).
* All 100 environment secrets.

Secrets are limited to 48 KB in size. To store larger secrets, see [AUTOTITLE](/actions/how-tos/security-for-github-actions/security-guides/using-secrets-in-github-actions#storing-large-secrets).

## When {% data variables.product.prodname_actions %} reads secrets

Organization and repository secrets are read when a workflow run is queued, and environment secrets are read when a job referencing the environment starts.

## Automatically redacted secrets

{% data variables.product.prodname_dotcom %} automatically redacts the following sensitive information from workflow logs.

> [!NOTE] If you would like other types of sensitive information to be automatically redacted, please reach out to us in our [community discussions](https://github.com/orgs/community/discussions?discussions_q=is%3Aopen+label%3AActions).

* 32-byte and 64-byte Azure keys
* Azure AD client app passwords
* Azure Cache keys
* Azure Container Registry keys
* Azure Function host keys
* Azure Search keys
* Database connection strings
* HTTP Bearer token headers
* JWTs
* NPM author tokens
* NuGet API keys
* v1 GitHub installation tokens
* v2 GitHub installation tokens (`ghp`, `gho`, `ghu`, `ghs`, `ghr`)
* v2 GitHub PATs

## Security

For security best practices using secrets, see [AUTOTITLE](/actions/reference/secure-use-reference#use-secrets-for-sensitive-information).
A: {
  "extractions": [
    {
      "security_advice": ">[!TIP]\n> To help ensure that {% data variables.product.prodname_dotcom %} redacts your secrets in logs correctly, avoid using structured data as the values of secrets.\n",
      "security_advice_attributes": {
        "type": "alert"
      }
    },
    {
      "security_advice": "For security best practices using secrets, see [AUTOTITLE](/actions/reference/secure-use-reference#use-secrets-for-sensitive-information).\n",
      "security_advice_attributes": {
        "type": "linked"
      }
    }
  ]
}

Q: ## Understanding the risk of script injections

When creating workflows, [custom actions](/actions/creating-actions/about-custom-actions), and [composite actions](/actions/creating-actions/creating-a-composite-action), you should always consider whether your code might execute untrusted input from attackers. This can occur when an attacker adds malicious commands and scripts to a context. When your workflow runs, those strings might be interpreted as code which is then executed on the runner.

Attackers can add their own malicious content to the [`github` context](/actions/learn-github-actions/contexts#github-context), which should be treated as potentially untrusted input. These contexts typically end with `body`, `default_branch`, `email`, `head_ref`, `label`, `message`, `name`, `page_name`,`ref`, and `title`. For example: `github.event.issue.title`, or `github.event.pull_request.body`.

You should ensure that these values do not flow directly into workflows, actions, API calls, or anywhere else where they could be interpreted as executable code. By adopting the same defensive programming posture you would use for any other privileged application code, you can help security harden your use of {% data variables.product.prodname_actions %}. For information on some of the steps an attacker could take, see [AUTOTITLE](/actions/security-guides/security-hardening-for-github-actions#potential-impact-of-a-compromised-runner).

In addition, there are other less obvious sources of potentially untrusted input, such as branch names and email addresses, which can be quite flexible in terms of their permitted content. For example, `zzz";echo${IFS}"hello";#` would be a valid branch name and would be a possible attack vector for a target repository.

The following sections explain how you can help mitigate the risk of script injection.

### Example of a script injection attack

A script injection attack can occur directly within a workflow's inline script. In the following example, an action uses an expression to test the validity of a pull request title, but also adds the risk of script injection:

{% raw %}

```yaml
      - name: Check PR title
        run: |
          title="${{ github.event.pull_request.title }}"
          if [[ $title =~ ^octocat ]]; then
          echo "PR title starts with 'octocat'"
          exit 0
          else
          echo "PR title did not start with 'octocat'"
          exit 1
          fi
```

{% endraw %}

This example is vulnerable to script injection because the `run` command executes within a temporary shell script on the runner. Before the shell script is run, the expressions inside {% raw %}`${{ }}`{% endraw %} are evaluated and then substituted with the resulting values, which can make it vulnerable to shell command injection.

To inject commands into this workflow, the attacker could create a pull request with a title of `a"; ls $GITHUB_WORKSPACE"`:

![Screenshot of the title of a pull request in edit mode. A new title has been entered in the field: a"; ls $GITHUB_WORKSPACE".](/assets/images/help/actions/example-script-injection-pr-title.png)

In this example, the `"` character is used to interrupt the {% raw %}`title="${{ github.event.pull_request.title }}"`{% endraw %} statement, allowing the `ls` command to be executed on the runner. You can see the output of the `ls` command in the log:

```shell
Run title="a"; ls $GITHUB_WORKSPACE""
README.md
code.yml
example.js
```

For best practices keeping runners secure, see [AUTOTITLE](/actions/reference/secure-use-reference#good-practices-for-mitigating-script-injection-attacks).
A: {
  "extractions": [
    {
      "security_advice": "When creating workflows, [custom actions](/actions/creating-actions/about-custom-actions), and [composite actions](/actions/creating-actions/creating-a-composite-action), you should always consider whether your code might execute untrusted input from attackers. This can occur when an attacker adds malicious commands and scripts to a context. When your workflow runs, those strings might be interpreted as code which is then executed on the runner.\n\nAttackers can add their own malicious content to the [`github` context](/actions/learn-github-actions/contexts#github-context), which should be treated as potentially untrusted input. These contexts typically end with `body`, `default_branch`, `email`, `head_ref`, `label`, `message`, `name`, `page_name`,`ref`, and `title`. For example: `github.event.issue.title`, or `github.event.pull_request.body`.\n\nYou should ensure that these values do not flow directly into workflows, actions, API calls, or anywhere else where they could be interpreted as executable code. By adopting the same defensive programming posture you would use for any other privileged application code, you can help security harden your use of {% data variables.product.prodname_actions %}. For information on some of the steps an attacker could take, see [AUTOTITLE](/actions/security-guides/security-hardening-for-github-actions#potential-impact-of-a-compromised-runner).\n\nIn addition, there are other less obvious sources of potentially untrusted input, such as branch names and email addresses, which can be quite flexible in terms of their permitted content. For example, `zzz\";echo${IFS}\"hello\";#` would be a valid branch name and would be a possible attack vector for a target repository.       \n",
      "security_advice_attributes": {
        "type": "textual"
      }
    },
    {
      "security_advice": "For best practices keeping runners secure, see [AUTOTITLE](/actions/reference/secure-use-reference#good-practices-for-mitigating-script-injection-attacks).\n",
      "security_advice_attributes": {
        "type": "linked"
      }
    }
  ]
}

Q: ## Requirements for self-hosted runner machines

You can use a machine as a self-hosted runner as long as it meets these requirements:

* You can install and run the self-hosted runner application on the machine. See [Supported operating systems](#supported-operating-systems) and [Supported processor architectures](#supported-processor-architectures).
* The machine can communicate with {% data variables.product.prodname_actions %}.
* The machine has enough hardware resources for the type of workflows you plan to run. The self-hosted runner application itself only requires minimal resources.
* If you want to run workflows that use Docker container actions or service containers, you must use a Linux machine and Docker must be installed.

### Supported operating systems

#### Linux

* Red Hat Enterprise Linux 8 or later
* CentOS 8 or later
* Oracle Linux 8 or later
* Fedora 29 or later
* Debian 10 or later
* Ubuntu 20.04 or later
* Linux Mint 20 or later
* openSUSE 15.2 or later
* SUSE Enterprise Linux (SLES) 15 SP2 or later

#### Windows

* Windows 10 64-bit
* Windows 11 64-bit
* Windows Server 2016 64-bit
* Windows Server 2019 64-bit
* Windows Server 2022 64-bit

#### macOS

* macOS 11.0 (Big Sur) or later

### Supported processor architectures

* `x64` - Linux, macOS, Windows.
* `ARM64` - Linux, macOS{% ifversion actions-windows-arm %}, Windows (currently in {% data variables.release-phases.public_preview %}){% endif %}.
* `ARM32` - Linux.

## Routing precedence for self-hosted runners

When routing a job to a self-hosted runner, {% data variables.product.prodname_dotcom %} looks for a runner that matches the job's `runs-on` labels and groups:

* If {% data variables.product.prodname_dotcom %} finds an online and idle runner that matches the job's `runs-on` labels and groups, the job is then assigned and sent to the runner.
  * If the runner doesn't pick up the assigned job within 60 seconds, the job is re-queued so that a new runner can accept it.
* If {% data variables.product.prodname_dotcom %} doesn't find an online and idle runner that matches the job's `runs-on` labels and groups, then the job will remain queued until a runner comes online.
* If the job remains queued for more than 24 hours, the job will fail.

## Autoscaling

You can automatically increase or decrease the number of self-hosted runners in your environment in response to the webhook events you receive with a particular label.

### Supported autoscaling solutions

{% ifversion fpt or ghec %}

{% data variables.product.prodname_dotcom %}-hosted runners inherently autoscale based on your needs. {% data variables.product.prodname_dotcom %}-hosted runners can be a low-maintenance and cost-effective alternative to developing or implementing autoscaling solutions. For more information, see [AUTOTITLE](/actions/using-github-hosted-runners/about-github-hosted-runners/about-github-hosted-runners).

{% endif %}

The [actions/actions-runner-controller](https://github.com/actions/actions-runner-controller) (ARC) project is a Kubernetes-based runner autoscaler. {% data variables.product.prodname_dotcom %} recommends ARC if the team deploying it has expert Kubernetes knowledge and experience.

For more information, see [AUTOTITLE](/actions/hosting-your-own-runners/managing-self-hosted-runners-with-actions-runner-controller/about-actions-runner-controller) and [AUTOTITLE](/actions/hosting-your-own-runners/managing-self-hosted-runners-with-actions-runner-controller/about-support-for-actions-runner-controller).

### Ephemeral runners for autoscaling

{% data variables.product.prodname_dotcom %} recommends implementing autoscaling with ephemeral self-hosted runners; autoscaling with persistent self-hosted runners is not recommended. In certain cases, {% data variables.product.prodname_dotcom %} cannot guarantee that jobs are not assigned to persistent runners while they are shut down. With ephemeral runners, this can be guaranteed because {% data variables.product.prodname_dotcom %} only assigns one job to a runner.

This approach allows you to manage your runners as ephemeral systems, since you can use automation to provide a clean environment for each job. This helps limit the exposure of any sensitive resources from previous jobs, and also helps mitigate the risk of a compromised runner receiving new jobs.

>[!WARNING]The runner application log files for ephemeral runners must be forwarded to an external log storage solution for troubleshooting and diagnostic purposes. While it is not required for ephemeral runners to be deployed, {% data variables.product.prodname_dotcom %} recommends ensuring runner logs are forwarded and preserved externally before deploying an ephemeral runner autoscaling solution in a production environment. For more information, see [AUTOTITLE](/actions/hosting-your-own-runners/managing-self-hosted-runners/monitoring-and-troubleshooting-self-hosted-runners#reviewing-the-self-hosted-runner-application-log-files).

To add an ephemeral runner to your environment, include the `--ephemeral` parameter when registering your runner using `config.sh`. For example:

```shell
./config.sh --url https://github.com/octo-org --token example-token --ephemeral
```

The {% data variables.product.prodname_actions %} service will then automatically de-register the runner after it has processed one job. You can then create your own automation that wipes the runner after it has been de-registered.

> [!NOTE]
> If a job is labeled for a certain type of runner, but none matching that type are available, the job does not immediately fail at the time of queueing. Instead, the job will remain queued until the 24 hour timeout period expires.

Alternatively, you can create ephemeral, just-in-time runners using the REST API. For more information, see [AUTOTITLE](/rest/actions/self-hosted-runners).

### Runner software updates on self-hosted runners

By default, self-hosted runners will automatically perform a software update whenever a new version of the runner software is available. If you use ephemeral runners in containers then this can lead to repeated software updates when a new runner version is released. Turning off automatic updates allows you to update the runner version on the container image directly on your own schedule.

To turn off automatic software updates and install software updates yourself, specify the `--disableupdate` flag when registering your runner using `config.sh`. For example:

```shell
./config.sh --url https://github.com/YOUR-ORGANIZATION --token EXAMPLE-TOKEN --disableupdate
```

If you disable automatic updates, you must still update your runner version regularly. New functionality in {% data variables.product.prodname_actions %} requires changes in both the {% data variables.product.prodname_actions %} service _and_ the runner software. The runner may not be able to correctly process jobs that take advantage of new features in {% data variables.product.prodname_actions %} without a software update.

If you disable automatic updates, you will be required to update your runner version within 30 days of a new version being made available. You may want to subscribe to notifications for releases in the [`actions/runner` repository](https://github.com/actions/runner/releases). For more information, see [AUTOTITLE](/account-and-profile/managing-subscriptions-and-notifications-on-github/setting-up-notifications/configuring-notifications#about-custom-notifications).

For instructions on how to install the latest runner version, see the installation instructions for [the latest release](https://github.com/actions/runner/releases).

{% data reusables.actions.self-hosted-runner-update-warning %}

### Webhooks for autoscaling

You can create your own autoscaling environment by using payloads received from the [`workflow_job`](/webhooks-and-events/webhooks/webhook-events-and-payloads#workflow_job) webhook. This webhook is available at the repository, organization, and enterprise levels, and the payload for this event contains an `action` key that corresponds to the stages of a workflow job's life-cycle; for example when jobs are `queued`, `in_progress`, and `completed`. You must then create your own scaling automation in response to these webhook payloads.

* For more information about the `workflow_job` webhook, see [AUTOTITLE](/webhooks-and-events/webhooks/webhook-events-and-payloads#workflow_job).
* To learn how to work with webhooks, see [AUTOTITLE](/webhooks).

### Authentication requirements

You can register and delete repository and organization self-hosted runners using [the API](/rest/actions/self-hosted-runners). To authenticate to the API, your autoscaling implementation can use an access token or a {% data variables.product.prodname_dotcom %} app.

Your access token will require the following scope:

* For private repositories, use an access token with the [`repo` scope](/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes).
* For public repositories, use an access token with the [`public_repo` scope](/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes).
* For organizations, use an access token with the [`admin:org` scope](/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes).

To authenticate using a {% data variables.product.prodname_dotcom %} App, it must be assigned the following permissions:

* For repositories, assign the `administration` permission.
* For organizations, assign the `organization_self_hosted_runners` permission.

You can register and delete enterprise self-hosted runners using [the API](/rest/actions/self-hosted-runners). To authenticate to the API, your autoscaling implementation can use an access token.

Your access token will require the `manage_runners:enterprise` scope.

## Communication

Self-hosted runners connect to {% ifversion fpt or ghec %}{% data variables.product.github %}{% else %}{% data variables.location.product_location_enterprise %}{% endif %} to receive job assignments and download new versions of the runner application.

{% data reusables.actions.runner-app-open-source %} {% ifversion fpt or ghec %} When a new version is released, the runner application automatically updates itself when a job is assigned to the runner, or within a week of release if the runner hasn't been assigned any jobs. {% else ifversion ghes %} When a new version is released, the runner application will automatically update within 24 hours.{% endif %}

### Requirements for communication{% ifversion fpt or ghec %} with {% data variables.product.github %}{% else %} with {% data variables.location.product_location_enterprise %}{% endif %}

* The self-hosted runner application must be running on the host machine to accept and run {% data variables.product.prodname_actions %} jobs.
{%- ifversion fpt or ghec %}
* The host machine must have appropriate network access with at least 70 kilobits per second upload and download speed.
* The host machine must be able to make outbound HTTPS connections over port 443.
* Depending on the function of the workflows assigned to your self-hosted runner, the host machine must be able to communicate with the {% data variables.product.github %} domains listed below.
{% else %}
* {% data variables.product.prodname_ghe_server %} must accept inbound connections from your runners over HTTP(S) at {% data variables.location.product_location_enterprise %}'s hostname and API subdomain, and your runners must allow outbound connections over HTTP(S) to {% data variables.location.product_location_enterprise %}'s hostname and API subdomain.
* For caching to work, the runner must be able to communicate with, and directly download content from, blob storage.
{% endif %}

{% ifversion fpt or ghec %}

### Accessible domains by function

{% data reusables.actions.domain-name-cname-recursive-firewall-rules %}

{% data reusables.actions.runner-essential-communications %}

In addition, your workflow may require access to other network resources.

If you use an IP address allow list for your {% data variables.product.prodname_dotcom %} organization or enterprise account, you must add your self-hosted runner's IP address to the allow list. See [Managing allowed IP addresses for your organization](/{% ifversion fpt %}enterprise-cloud@latest/{% endif %}/organizations/keeping-your-organization-secure/managing-allowed-ip-addresses-for-your-organization#using-github-actions-with-an-ip-allow-list) or [Enforcing policies for security settings in your enterprise](/{% ifversion fpt %}enterprise-cloud@latest/{% endif %}admin/policies/enforcing-policies-for-your-enterprise/enforcing-policies-for-security-settings-in-your-enterprise){% ifversion fpt %} in the {% data variables.product.prodname_ghe_cloud %} documentation.{% else %}.{% endif %}

{% else %}

### Communication with {% data variables.product.prodname_dotcom_the_website %}

Self-hosted runners do not need to connect to {% data variables.product.prodname_dotcom_the_website %} unless you have enabled automatic access to {% data variables.product.prodname_dotcom_the_website %} actions for {% data variables.product.prodname_ghe_server %}. For more information, see [AUTOTITLE](/admin/github-actions/managing-access-to-actions-from-githubcom/about-using-actions-in-your-enterprise).

If you want your runner to connect to {% data variables.product.prodname_dotcom_the_website %}, the host machine must be able to make outbound HTTP connections over port 80, or HTTPS connections over port 443. To ensure connectivity over HTTPS, configure TLS for {% data variables.product.prodname_ghe_server %}. See [AUTOTITLE](/enterprise-server@latest/admin/configuration/hardening-security-for-your-enterprise/configuring-tls).

If you have enabled automatic access to {% data variables.product.prodname_dotcom_the_website %} actions, then the self-hosted runner will connect directly to {% data variables.product.prodname_dotcom_the_website %} to download actions. You must ensure that the machine has the appropriate network access to communicate with the {% data variables.product.prodname_dotcom %} URLs listed below.

```shell copy
github.com
api.github.com
codeload.github.com
```

You can use the REST API to get meta information about {% data variables.product.company_short %}, including the IP addresses and domain details for {% data variables.product.company_short %} services. The `actions_inbound` section of the API supports both fully qualified and wildcard domains. Fully qualified domains specify a complete domain name (e.g., `example.github.com`), while wildcard domains use a `*` to represent multiple possible subdomains (e.g., `*.github.com`). An example of the self-hosted runner requirements using wildcard domains has been listed below. For more information, see [AUTOTITLE](/rest/meta/meta).

```shell copy
github.com
*.github.com
*.githubusercontent.com
ghcr.io
```

{% data reusables.actions.domain-name-cname-recursive-firewall-rules %}

{% endif %}
A:

´´´

This just sucks and is not really well suited for our purpose!

With some fixes in place, we now have a nicer prompt:

{
  "key": "idx-0",
  "request": {
    "contents": [
      {
        "role": "user",
        "parts": [
          {
            "text": "# SecurityAdviceExtract\n\n## Task Description\nYou are a cybersecurity documentation expert specialized in identifying and categorizing security advice within GitHub documentation files (Markdown). Your goal is to extract text segments that strictly fit the definition of \"Security Advice\" for a developer audience. Extract characters, emotions, and relationships in order of appearance. Use exact text for extractions. Do not paraphrase or overlap entities. Provide meaningful attributes for each entity to add context.\n\n### Definition of Security Advice\nA text segment qualifies as **security_advice_body** if it contains:\n1.  A specific security risk, vulnerability, or threat.\n2.  A sequence of actions, commands, or configuration steps to achieve an outcome that reduces or mitigates that risk.\n3.  Advice targeted at solving one specific problem.\n\n### Attributes\nThere are currently $3$ distinct single class attribute types. Assign one on the following:\n- **alert** use the markdown syntax for blockquotes, e.g. `> [!Alert] \\n > Do not enable debug in production`\n- **linked** for security advices that point to 3rd party resources/websites\n- **textual** plain written security advices\n\n### Critical Rule: EXACT MATCH ONLY\nThe extraction library uses substring matching. You must extract the text **exactly as it appears** in the source markdown.\n- **DO NOT** fix typos.\n- **DO NOT** rephrase sentences.\n- **DO NOT** change punctuation.\n- **DO NOT** expand abbreviations.\n- **DO NOT** remove Markdown syntax (bolding, code ticks, links).\n- **DO NOT** render or remove Liquid templates (e.g., `{% data ... %}`).\n\n## Examples\n\nThe examples follow a Question (Q) and Answer (A) format. Since the Questions consist of raw Markdown documents, each Question begins with the delimiter <<<md and ends with >>>.\n\n\nQ:\n<<<md\n## Naming your secrets\n\n>[!TIP]\n> To help ensure that {% data variables.product.prodname_dotcom %} redacts your secrets in logs correctly, avoid using structured data as the values of secrets.\n\nThe following rules apply to secret names:\n\n{% data reusables.actions.actions-secrets-and-variables-naming %}\n\n{% data reusables.codespaces.secret-precedence %} Similarly, if an organization, repository, and environment all have a secret with the same name, the environment-level secret takes precedence.\n\n## Limits for secrets\n\nYou can store up to 1,000 organization secrets, 100 repository secrets, and 100 environment secrets.\n\nA workflow created in a repository can access the following number of secrets:\n\n* All 100 repository secrets.\n* If the repository is assigned access to more than 100 organization secrets, the workflow can only use the first 100 organization secrets (sorted alphabetically by secret name).\n* All 100 environment secrets.\n\nSecrets are limited to 48 KB in size. To store larger secrets, see [AUTOTITLE](/actions/how-tos/security-for-github-actions/security-guides/using-secrets-in-github-actions#storing-large-secrets).\n\n## When {% data variables.product.prodname_actions %} reads secrets\n\nOrganization and repository secrets are read when a workflow run is queued, and environment secrets are read when a job referencing the environment starts.\n\n## Automatically redacted secrets\n\n{% data variables.product.prodname_dotcom %} automatically redacts the following sensitive information from workflow logs.\n\n> [!NOTE] If you would like other types of sensitive information to be automatically redacted, please reach out to us in our [community discussions](https://github.com/orgs/community/discussions?discussions_q=is%3Aopen+label%3AActions).\n\n* 32-byte and 64-byte Azure keys\n* Azure AD client app passwords\n* Azure Cache keys\n* Azure Container Registry keys\n* Azure Function host keys\n* Azure Search keys\n* Database connection strings\n* HTTP Bearer token headers\n* JWTs\n* NPM author tokens\n* NuGet API keys\n* v1 GitHub installation tokens\n* v2 GitHub installation tokens (`ghp`, `gho`, `ghu`, `ghs`, `ghr`)\n* v2 GitHub PATs\n\n## Security\n\nFor security best practices using secrets, see [AUTOTITLE](/actions/reference/secure-use-reference#use-secrets-for-sensitive-information).\n>>>\n\nA:\n{\n  \"extractions\": [\n    {\n      \"security_advice\": \">[!TIP]\\n> To help ensure that {% data variables.product.prodname_dotcom %} redacts your secrets in logs correctly, avoid using structured data as the values of secrets.\\n\",\n      \"security_advice_attributes\": {\n        \"type\": \"alert\"\n      }\n    },\n    {\n      \"security_advice\": \"For security best practices using secrets, see [AUTOTITLE](/actions/reference/secure-use-reference#use-secrets-for-sensitive-information).\\n\",\n      \"security_advice_attributes\": {\n        \"type\": \"linked\"\n      }\n    }\n  ]\n}\n\nQ:\n<<<md\n## Understanding the risk of script injections\n\nWhen creating workflows, [custom actions](/actions/creating-actions/about-custom-actions), and [composite actions](/actions/creating-actions/creating-a-composite-action), you should always consider whether your code might execute untrusted input from attackers. This can occur when an attacker adds malicious commands and scripts to a context. When your workflow runs, those strings might be interpreted as code which is then executed on the runner.\n\nAttackers can add their own malicious content to the [`github` context](/actions/learn-github-actions/contexts#github-context), which should be treated as potentially untrusted input. These contexts typically end with `body`, `default_branch`, `email`, `head_ref`, `label`, `message`, `name`, `page_name`,`ref`, and `title`. For example: `github.event.issue.title`, or `github.event.pull_request.body`.\n\nYou should ensure that these values do not flow directly into workflows, actions, API calls, or anywhere else where they could be interpreted as executable code. By adopting the same defensive programming posture you would use for any other privileged application code, you can help security harden your use of {% data variables.product.prodname_actions %}. For information on some of the steps an attacker could take, see [AUTOTITLE](/actions/security-guides/security-hardening-for-github-actions#potential-impact-of-a-compromised-runner).\n\nIn addition, there are other less obvious sources of potentially untrusted input, such as branch names and email addresses, which can be quite flexible in terms of their permitted content. For example, `zzz\";echo${IFS}\"hello\";#` would be a valid branch name and would be a possible attack vector for a target repository.\n\nThe following sections explain how you can help mitigate the risk of script injection.\n\n### Example of a script injection attack\n\nA script injection attack can occur directly within a workflow's inline script. In the following example, an action uses an expression to test the validity of a pull request title, but also adds the risk of script injection:\n\n{% raw %}\n\n```yaml\n      - name: Check PR title\n        run: |\n          title=\"${{ github.event.pull_request.title }}\"\n          if [[ $title =~ ^octocat ]]; then\n          echo \"PR title starts with 'octocat'\"\n          exit 0\n          else\n          echo \"PR title did not start with 'octocat'\"\n          exit 1\n          fi\n```\n\n{% endraw %}\n\nThis example is vulnerable to script injection because the `run` command executes within a temporary shell script on the runner. Before the shell script is run, the expressions inside {% raw %}`${{ }}`{% endraw %} are evaluated and then substituted with the resulting values, which can make it vulnerable to shell command injection.\n\nTo inject commands into this workflow, the attacker could create a pull request with a title of `a\"; ls $GITHUB_WORKSPACE\"`:\n\n![Screenshot of the title of a pull request in edit mode. A new title has been entered in the field: a\"; ls $GITHUB_WORKSPACE\".](/assets/images/help/actions/example-script-injection-pr-title.png)\n\nIn this example, the `\"` character is used to interrupt the {% raw %}`title=\"${{ github.event.pull_request.title }}\"`{% endraw %} statement, allowing the `ls` command to be executed on the runner. You can see the output of the `ls` command in the log:\n\n```shell\nRun title=\"a\"; ls $GITHUB_WORKSPACE\"\"\nREADME.md\ncode.yml\nexample.js\n```\n\nFor best practices keeping runners secure, see [AUTOTITLE](/actions/reference/secure-use-reference#good-practices-for-mitigating-script-injection-attacks).\n>>>\n\nA:\n{\n  \"extractions\": [\n    {\n      \"security_advice\": \"When creating workflows, [custom actions](/actions/creating-actions/about-custom-actions), and [composite actions](/actions/creating-actions/creating-a-composite-action), you should always consider whether your code might execute untrusted input from attackers. This can occur when an attacker adds malicious commands and scripts to a context. When your workflow runs, those strings might be interpreted as code which is then executed on the runner.\\n\\nAttackers can add their own malicious content to the [`github` context](/actions/learn-github-actions/contexts#github-context), which should be treated as potentially untrusted input. These contexts typically end with `body`, `default_branch`, `email`, `head_ref`, `label`, `message`, `name`, `page_name`,`ref`, and `title`. For example: `github.event.issue.title`, or `github.event.pull_request.body`.\\n\\nYou should ensure that these values do not flow directly into workflows, actions, API calls, or anywhere else where they could be interpreted as executable code. By adopting the same defensive programming posture you would use for any other privileged application code, you can help security harden your use of {% data variables.product.prodname_actions %}. For information on some of the steps an attacker could take, see [AUTOTITLE](/actions/security-guides/security-hardening-for-github-actions#potential-impact-of-a-compromised-runner).\\n\\nIn addition, there are other less obvious sources of potentially untrusted input, such as branch names and email addresses, which can be quite flexible in terms of their permitted content. For example, `zzz\\\";echo${IFS}\\\"hello\\\";#` would be a valid branch name and would be a possible attack vector for a target repository.       \\n\",\n      \"security_advice_attributes\": {\n        \"type\": \"textual\"\n      }\n    },\n    {\n      \"security_advice\": \"For best practices keeping runners secure, see [AUTOTITLE](/actions/reference/secure-use-reference#good-practices-for-mitigating-script-injection-attacks).\\n\",\n      \"security_advice_attributes\": {\n        \"type\": \"linked\"\n      }\n    }\n  ]\n}\n\nQ:\n<<<md\n> [!NOTE]\n> This feature is currently in {% data variables.release-phases.public_preview %} and is subject to change.\n\n{% data reusables.actions.enterprise-github-hosted-runners %}\n\n## About container customization\n\n{% data variables.product.prodname_actions %} allows you to run a job within a container, using the `container:` statement in your workflow file. For more information, see [AUTOTITLE](/actions/using-jobs/running-jobs-in-a-container). To process container-based jobs, the self-hosted runner creates a container for each job.\n\n{% data variables.product.prodname_actions %} supports commands that let you customize the way your containers are created by the self-hosted runner. For example, you can use these commands to manage the containers through Kubernetes or Podman, and you can also customize the `docker run` or `docker create` commands used to invoke the container. The customization commands are run by a script, which is automatically triggered when a specific environment variable is set on the runner. For more information, see [Triggering the customization script](#triggering-the-customization-script) below.\n\nThis customization is only available for Linux-based self-hosted runners, and root user access is not required.\n\n## Container customization commands\n\n{% data variables.product.prodname_actions %} includes the following commands for container customization:\n\n* [`prepare_job`](/actions/hosting-your-own-runners/managing-self-hosted-runners/customizing-the-containers-used-by-jobs#prepare_job): Called when a job is started.\n* [`cleanup_job`](/actions/hosting-your-own-runners/managing-self-hosted-runners/customizing-the-containers-used-by-jobs#cleanup_job): Called at the end of a job.\n* [`run_container_step`](/actions/hosting-your-own-runners/managing-self-hosted-runners/customizing-the-containers-used-by-jobs#run_container_step): Called once for each container action in the job.\n* [`run_script_step`](/actions/hosting-your-own-runners/managing-self-hosted-runners/customizing-the-containers-used-by-jobs#run_script_step): Runs any step that is not a container action.\n\nEach of these customization commands must be defined in its own JSON file. The file name must match the command name, with the extension `.json`. For example, the `prepare_job` command is defined in `prepare_job.json`. These JSON files will then be run together on the self-hosted runner, as part of the main `index.js` script. This process is described in more detail in [Generating the customization script](#generating-the-customization-script).\n\nThese commands also include configuration arguments, explained below in more detail.\n\n### `prepare_job`\n\nThe `prepare_job` command is called when a job is started. {% data variables.product.prodname_actions %} passes in any job or service containers the job has. This command will be called if you have any service or job containers in the job.\n\n{% data variables.product.prodname_actions %} assumes that you will do the following tasks in the `prepare_job` command:\n\n* Prune anything from previous jobs, if needed.\n* Create a network, if needed.\n* Pull the job and service containers.\n* Start the job container.\n* Start the service containers.\n* Write to the response file any information that {% data variables.product.prodname_actions %} will need:\n  * Required: State whether the container is an `alpine` linux container (using the `isAlpine` boolean).\n  * Optional: Any context fields you want to set on the job context, otherwise they will be unavailable for users to use. For more information, see [AUTOTITLE](/actions/learn-github-actions/contexts#job-context).\n* Return `0` when the health checks have succeeded and the job/service containers are started.\n\n#### Arguments for `prepare_job`\n\n* `jobContainer`: **Optional**. An object containing information about the specified job container.\n  * `image`: **Required**. A string containing the Docker image.\n  * `workingDirectory`: **Required**. A string containing the absolute path of the working directory.\n  * `createOptions`: **Optional**. The optional _create_ options specified in the YAML. For more information, see [AUTOTITLE](/actions/using-jobs/running-jobs-in-a-container#example-running-a-job-within-a-container).\n  * `environmentVariables`: **Optional**. Sets a map of key environment variables.\n  * `userMountVolumes`: **Optional**. An array of user mount volumes set in the YAML. For more information, see [AUTOTITLE](/actions/using-jobs/running-jobs-in-a-container#example-running-a-job-within-a-container).\n    * `sourceVolumePath`: **Required**. The source path to the volume that will be mounted into the Docker container.\n    * `targetVolumePath`: **Required**. The target path to the volume that will be mounted into the Docker container.\n    * `readOnly`: **Required**. Determines whether or not the mount should be read-only.\n  * `systemMountVolumes`: **Required**. An array of mounts to mount into the container, same fields as above.\n    * `sourceVolumePath`: **Required**. The source path to the volume that will be mounted into the Docker container.\n    * `targetVolumePath`: **Required**. The target path to the volume that will be mounted into the Docker container.\n    * `readOnly`: **Required**. Determines whether or not the mount should be read-only.\n  * `registry` **Optional**. The Docker registry credentials for a private container registry.\n    * `username`: **Optional**. The username of the registry account.\n    * `password`: **Optional**. The password to the registry account.\n    * `serverUrl`: **Optional**. The registry URL.\n  * `portMappings`: **Optional**. A key value hash of _source:target_ ports to map into the container.\n* `services`: **Optional**. An array of service containers to spin up.\n  * `contextName`: **Required**. The name of the service in the Job context.\n  * `image`: **Required**. A string containing the Docker image.\n  * `createOptions`: **Optional**. The optional _create_ options specified in the YAML. For more information, see [AUTOTITLE](/actions/using-jobs/running-jobs-in-a-container#example-running-a-job-within-a-container).\n  * `environmentVariables`: **Optional**. Sets a map of key environment variables.\n  * `userMountVolumes`: **Optional**. An array of mounts to mount into the container, same fields as above.\n    * `sourceVolumePath`: **Required**. The source path to the volume that will be mounted into the Docker container.\n    * `targetVolumePath`: **Required**. The target path to the volume that will be mounted into the Docker container.\n    * `readOnly`: **Required**. Determines whether or not the mount should be read-only.\n  * `registry` **Optional**. The Docker registry credentials for the private container registry.\n    * `username`: **Optional**. The username of the registry account.\n    * `password`: **Optional**. The password to the registry account.\n    * `serverUrl`: **Optional**. The registry URL.\n  * `portMappings`: **Optional**. A key value hash of _source:target_ ports to map into the container.\n\n#### Example input for `prepare_job`\n\n```json copy\n{\n  \"command\": \"prepare_job\",\n  \"responseFile\": \"/users/octocat/runner/_work/{guid}.json\",\n  \"state\": {},\n  \"args\": {\n    \"jobContainer\": {\n      \"image\": \"node:18\"\n      \"workingDirectory\": \"/__w/octocat-test2/octocat-test2\",\n      \"createOptions\": \"--cpus 1\",\n      \"environmentVariables\": {\n        \"NODE_ENV\": \"development\"\n      },\n      \"userMountVolumes\": [\n        {\n          \"sourceVolumePath\": \"my_docker_volume\",\n          \"targetVolumePath\": \"/volume_mount\",\n          \"readOnly\": false\n        }\n      ],\n      \"systemMountVolumes\": [\n        {\n          \"sourceVolumePath\": \"/home/octocat/git/runner/_layout/_work\",\n          \"targetVolumePath\": \"/__w\",\n          \"readOnly\": false\n        },\n        {\n          \"sourceVolumePath\": \"/home/octocat/git/runner/_layout/externals\",\n          \"targetVolumePath\": \"/__e\",\n          \"readOnly\": true\n        },\n        {\n          \"sourceVolumePath\": \"/home/octocat/git/runner/_layout/_work/_temp\",\n          \"targetVolumePath\": \"/__w/_temp\",\n          \"readOnly\": false\n        },\n        {\n          \"sourceVolumePath\": \"/home/octocat/git/runner/_layout/_work/_actions\",\n          \"targetVolumePath\": \"/__w/_actions\",\n          \"readOnly\": false\n        },\n        {\n          \"sourceVolumePath\": \"/home/octocat/git/runner/_layout/_work/_tool\",\n          \"targetVolumePath\": \"/__w/_tool\",\n          \"readOnly\": false\n        },\n        {\n          \"sourceVolumePath\": \"/home/octocat/git/runner/_layout/_work/_temp/_github_home\",\n          \"targetVolumePath\": \"/github/home\",\n          \"readOnly\": false\n        },\n        {\n          \"sourceVolumePath\": \"/home/octocat/git/runner/_layout/_work/_temp/_github_workflow\",\n          \"targetVolumePath\": \"/github/workflow\",\n          \"readOnly\": false\n        }\n      ],\n      \"registry\": {\n        \"username\": \"octocat\",\n        \"password\": \"examplePassword\",\n        \"serverUrl\": \"https://index.docker.io/v1\"\n      },\n      \"portMappings\": { \"80\": \"801\" }\n    },\n    \"services\": [\n      {\n        \"contextName\": \"redis\",\n        \"image\": \"redis\",\n        \"createOptions\": \"--cpus 1\",\n        \"environmentVariables\": {},\n        \"userMountVolumes\": [],\n        \"portMappings\": { \"80\": \"801\" },\n        \"registry\": {\n          \"username\": \"octocat\",\n          \"password\": \"examplePassword\",\n          \"serverUrl\": \"https://index.docker.io/v1\"\n        }\n      }\n    ]\n  }\n}\n```\n\n#### Example output for `prepare_job`\n\nThis example output is the contents of the `responseFile` defined in the input above.\n\n```json copy\n{\n  \"state\": {\n    \"network\": \"example_network_53269bd575972817b43f7733536b200c\",\n    \"jobContainer\": \"82e8219701fe096a35941d869cf3d71af1d943b5d8bdd718857fb87ac3042480\",\n    \"serviceContainers\": {\n      \"redis\": \"60972d9aa486605e66b0dad4abb678dc3d9116f536579e418176eedb8abb9105\"\n    }\n  },\n  \"context\": {\n    \"container\": {\n>>>\n\nA:\n"
          }
        ]
      }
    ],
    "generationConfig": {
      "responseMimeType": "application/json",
      "responseSchema": {
        "type": "object",
        "properties": {
          "extractions": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "security_advice": {
                  "type": "string"
                },
                "security_advice_attributes": {
                  "type": "object",
                  "properties": {
                    "type": {
                      "type": "string"
                    }
                  },
                  "nullable": true
                }
              }
            }
          }
        },
        "required": [
          "extractions"
        ]
      },
      "temperature": 0
    }
  }
}



------ How much tokens/chars do we actually have?

```
(extraction) root ➜ /workspaces/github-best-pratices/extraction/gh-docs-2026-02-19 (main) $ fd -g "*.md" -E "index.md" content/actions/ | wc -l
200
```

```
(extraction) root ➜ /workspaces/github-best-pratices/extraction/gh-docs-2026-02-19 (main) $ fd -g "*.md" content/actions/ -x wc -w | sort -nr |
 head -n 10
19504 content/actions/reference/workflows-and-actions/workflow-syntax.md
10418 content/actions/reference/workflows-and-actions/events-that-trigger-workflows.md
7055 content/actions/reference/workflows-and-actions/contexts.md
5829 content/actions/tutorials/use-actions-runner-controller/deploy-runner-scale-sets.md
4683 content/actions/tutorials/migrate-to-github-actions/automated-migrations/azure-devops-migration.md
4519 content/actions/reference/security/secure-use.md
4356 content/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow.md
4047 content/actions/reference/workflows-and-actions/workflow-commands.md
3903 content/actions/tutorials/migrate-to-github-actions/automated-migrations/gitlab-migration.md
3765 content/actions/tutorials/migrate-to-github-actions/automated-migrations/bamboo-migration.md

(extraction) root ➜ /workspaces/github-best-pratices/extraction/gh-docs-2026-02-19 (main) $ fd -g "*.md" content/actions/ -x wc -c | sort -nr |
 head -n 10
206159 content/actions/reference/workflows-and-actions/workflow-syntax.md
96031 content/actions/reference/workflows-and-actions/contexts.md
91884 content/actions/reference/workflows-and-actions/events-that-trigger-workflows.md
52941 content/actions/tutorials/use-actions-runner-controller/deploy-runner-scale-sets.md
49423 content/actions/reference/workflows-and-actions/variables.md
40588 content/actions/tutorials/migrate-to-github-actions/automated-migrations/azure-devops-migration.md
36885 content/actions/tutorials/migrate-to-github-actions/automated-migrations/gitlab-migration.md
35236 content/actions/reference/security/secure-use.md
35200 content/actions/reference/security/oidc.md
33671 content/actions/tutorials/migrate-to-github-actions/automated-migrations/bamboo-migration.md
```

Tool recommends (after also removing redundant spaces etc) $2000$ .... 



```
(extraction) root ➜ /workspaces/github-best-pratices/extraction (main) $ uv run main.py
INFO:__main__:Using repo=/workspaces/github-best-pratices/extraction/gh-docs-2026-02-19/content
INFO:__main__:Using version=/workspaces/github-best-pratices/extraction/experiments/test8_clean_sheet_def
INFO:__main__:Added 2 examples
INFO:__main__:Batching status False
INFO:absl:Loaded provider plugin: gemini
INFO:absl:Loaded provider plugin: ollama
INFO:absl:Loaded provider plugin: openai
INFO:absl:Starting sequential extraction passes for improved recall with 2 passes.
INFO:absl:Starting extraction pass 1 of 2
LangExtract: model=gemini-2.5-flash, current=28,631 chars, processed=0 chars:  [00:00]INFO:google_genai.models:AFC is enabled with max remote calls: 10.
INFO:httpx:HTTP Request: POST https://us-east1-aiplatform.googleapis.com/v1beta1/projects/gh-docs-no-org/locations/us-east1/publishers/google/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"
INFO:absl:Statistics:
{
  "cache_tokens_details": [
    {
      "modality": "TEXT",
      "token_count": 5906
    }
  ],
  "cached_content_token_count": 5906,
  "candidates_token_count": 1418,
  "candidates_tokens_details": [
    {
      "modality": "TEXT",
      "token_count": 1418
    }
  ],
  "prompt_token_count": 6053,
  "prompt_tokens_details": [
    {
      "modality": "TEXT",
      "token_count": 6053
    }
  ],
  "thoughts_token_count": 1525,
  "tool_use_prompt_token_count": null,
  "tool_use_prompt_tokens_details": null,
  "total_token_count": 8996,
  "traffic_type": "ON_DEMAND"
}
INFO:google_genai.models:AFC is enabled with max remote calls: 10.
INFO:httpx:HTTP Request: POST https://us-east1-aiplatform.googleapis.com/v1beta1/projects/gh-docs-no-org/locations/us-east1/publishers/google/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"
INFO:absl:Statistics:
{
  "cache_tokens_details": null,
  "cached_content_token_count": null,
  "candidates_token_count": 139,
  "candidates_tokens_details": [
    {
      "modality": "TEXT",
      "token_count": 139
    }
  ],
  "prompt_token_count": 5789,
  "prompt_tokens_details": [
    {
      "modality": "TEXT",
      "token_count": 5789
    }
  ],
  "thoughts_token_count": 696,
  "tool_use_prompt_token_count": null,
  "tool_use_prompt_tokens_details": null,
  "total_token_count": 6624,
  "traffic_type": "ON_DEMAND"
}
LangExtract: model=gemini-2.5-flash, current=28,631 chars, processed=0 chars:  [00:15]
INFO:absl:Starting extraction pass 2 of 2
INFO:google_genai.models:AFC is enabled with max remote calls: 10.
INFO:httpx:HTTP Request: POST https://us-east1-aiplatform.googleapis.com/v1beta1/projects/gh-docs-no-org/locations/us-east1/publishers/google/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"
INFO:absl:Statistics:
{
  "cache_tokens_details": [
    {
      "modality": "TEXT",
      "token_count": 5906
    }
  ],
  "cached_content_token_count": 5906,
  "candidates_token_count": 1418,
  "candidates_tokens_details": [
    {
      "modality": "TEXT",
      "token_count": 1418
    }
  ],
  "prompt_token_count": 6053,
  "prompt_tokens_details": [
    {
      "modality": "TEXT",
      "token_count": 6053
    }
  ],
  "thoughts_token_count": 1525,
  "tool_use_prompt_token_count": null,
  "tool_use_prompt_tokens_details": null,
  "total_token_count": 8996,
  "traffic_type": "ON_DEMAND"
}
INFO:google_genai.models:AFC is enabled with max remote calls: 10.
INFO:httpx:HTTP Request: POST https://us-east1-aiplatform.googleapis.com/v1beta1/projects/gh-docs-no-org/locations/us-east1/publishers/google/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"
INFO:absl:Statistics:
{
  "cache_tokens_details": null,
  "cached_content_token_count": null,
  "candidates_token_count": 139,
  "candidates_tokens_details": [
    {
      "modality": "TEXT",
      "token_count": 139
    }
  ],
  "prompt_token_count": 5789,
  "prompt_tokens_details": [
    {
      "modality": "TEXT",
      "token_count": 5789
    }
  ],
  "thoughts_token_count": 696,
  "tool_use_prompt_token_count": null,
  "tool_use_prompt_tokens_details": null,
  "total_token_count": 6624,
  "traffic_type": "ON_DEMAND"
}
INFO:absl:Sequential extraction passes completed.
Task actions/reference/runners/self-hosted-runners.md      
    Extractions:
    Extraction(extraction_class='security_advice', extraction_text='GitHub recommends implementing autoscaling with ephemeral self-hosted runners; autoscaling with persistent self-hosted runners is not recommended. In certain cases, GitHub cannot guarantee that jobs are not assigned to persistent runners while they are shut down. With ephemeral runners, this can be guaranteed because GitHub only assigns one job to a runner.\n', char_interval=CharInterval(start_pos=6084, end_pos=6443), alignment_status=<AlignmentStatus.MATCH_EXACT: 'match_exact'>, extraction_index=1, group_index=0, description=None, attributes={'type': 'textual'})
Extraction(extraction_class='security_advice', extraction_text='This approach allows you to manage your runners as ephemeral systems, since you can use automation to provide a clean environment for each job. This helps limit the exposure of any sensitive resources from previous jobs, and also helps mitigate the risk of a compromised runner receiving new jobs.\n', char_interval=CharInterval(start_pos=6445, end_pos=6742), alignment_status=<AlignmentStatus.MATCH_EXACT: 'match_exact'>, extraction_index=2, group_index=1, description=None, attributes={'type': 'textual'})
Extraction(extraction_class='security_advice', extraction_text='> [!WARNING]The runner application log files for ephemeral runners must be forwarded to an external log storage solution for troubleshooting and diagnostic purposes. While it is not required for ephemeral runners to be deployed, GitHub recommends ensuring runner logs are forwarded and preserved externally before deploying an ephemeral runner autoscaling solution in a production environment. For more information, see [Monitoring and troubleshooting self-hosted runners](/en/actions/hosting-your-own-runners/managing-self-hosted-runners/monitoring-and-troubleshooting-self-hosted-runners#reviewing-the-self-hosted-runner-application-log-files).\n', char_interval=CharInterval(start_pos=6744, end_pos=6745), alignment_status=<AlignmentStatus.MATCH_LESSER: 'match_lesser'>, extraction_index=3, group_index=2, description=None, attributes={'type': 'alert'})
Extraction(extraction_class='security_advice', extraction_text='To add an ephemeral runner to your environment, include the `--ephemeral` parameter when registering your runner using `config.sh`.\n', char_interval=CharInterval(start_pos=7393, end_pos=7524), alignment_status=<AlignmentStatus.MATCH_EXACT: 'match_exact'>, extraction_index=4, group_index=3, description=None, attributes={'type': 'textual'})
Extraction(extraction_class='security_advice', extraction_text='You can then create your own automation that wipes the runner after it has been de-registered.\n', char_interval=CharInterval(start_pos=7739, end_pos=7833), alignment_status=<AlignmentStatus.MATCH_EXACT: 'match_exact'>, extraction_index=5, group_index=4, description=None, attributes={'type': 'textual'})
Extraction(extraction_class='security_advice', extraction_text='To turn off automatic software updates and install software updates yourself, specify the `--disableupdate` flag when registering your runner using `config.sh`.\n', char_interval=CharInterval(start_pos=8716, end_pos=8876), alignment_status=<AlignmentStatus.MATCH_EXACT: 'match_exact'>, extraction_index=6, group_index=5, description=None, attributes={'type': 'textual'})
Extraction(extraction_class='security_advice', extraction_text='If you disable automatic updates, you must still update your runner version regularly. New functionality in GitHub Actions requires changes in both the GitHub Actions service *and* the runner software. The runner may not be able to correctly process jobs that take advantage of new features in GitHub Actions without a software update.\n', char_interval=CharInterval(start_pos=8998, end_pos=9333), alignment_status=<AlignmentStatus.MATCH_EXACT: 'match_exact'>, extraction_index=7, group_index=6, description=None, attributes={'type': 'textual'})
Extraction(extraction_class='security_advice', extraction_text='If you disable automatic updates, you will be required to update your runner version within 30 days of a new version being made available. You may want to subscribe to notifications for releases in the [`actions/runner` repository](https://github.com/actions/runner/releases). For more information, see [Configuring notifications](/en/account-and-profile/managing-subscriptions-and-notifications-on-github/setting-up-notifications/configuring-notifications#about-custom-notifications).\n', char_interval=CharInterval(start_pos=9335, end_pos=9820), alignment_status=<AlignmentStatus.MATCH_EXACT: 'match_exact'>, extraction_index=8, group_index=7, description=None, attributes={'type': 'textual'})
Extraction(extraction_class='security_advice', extraction_text='> [!WARNING] Any updates released for the software, including major, minor, or patch releases, are considered as an available update. If you do not perform a software update within 30 days, the GitHub Actions service will not queue jobs to your runner. In addition, if a critical security update is required, the GitHub Actions service will not queue jobs to your runner until it has been updated.\n', char_interval=CharInterval(start_pos=9989, end_pos=9990), alignment_status=<AlignmentStatus.MATCH_LESSER: 'match_lesser'>, extraction_index=9, group_index=8, description=None, attributes={'type': 'alert'})
Extraction(extraction_class='security_advice', extraction_text='Your access token will require the following scope:\n* For private repositories, use an access token with the [`repo` scope](/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes).\n* For public repositories, use an access token with the [`public_repo` scope](/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes).\n* For organizations, use an access token with the [`admin:org` scope](/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes).\n', char_interval=CharInterval(start_pos=11732, end_pos=12247), alignment_status=<AlignmentStatus.MATCH_EXACT: 'match_exact'>, extraction_index=10, group_index=9, description=None, attributes={'type': 'textual'})
Extraction(extraction_class='security_advice', extraction_text='To authenticate using a GitHub App, it must be assigned the following permissions:\n* For repositories, assign the `administration` permission.\n* For organizations, assign the `organization_self_hosted_runners` permission.\n', char_interval=CharInterval(start_pos=12249, end_pos=12471), alignment_status=<AlignmentStatus.MATCH_EXACT: 'match_exact'>, extraction_index=11, group_index=10, description=None, attributes={'type': 'textual'})
Extraction(extraction_class='security_advice', extraction_text='Your access token will require the `manage_runners:enterprise` scope.\n', char_interval=CharInterval(start_pos=12673, end_pos=12742), alignment_status=<AlignmentStatus.MATCH_EXACT: 'match_exact'>, extraction_index=12, group_index=11, description=None, attributes={'type': 'textual'})
Extraction(extraction_class='security_advice', extraction_text="If you use an IP address allow list for your GitHub organization or enterprise account, you must add your self-hosted runner's IP address to the allow list. See [Managing allowed IP addresses for your organization](/en/enterprise-cloud@latest/organizations/keeping-your-organization-secure/managing-allowed-ip-addresses-for-your-organization#using-github-actions-with-an-ip-allow-list) or [Enforcing policies for security settings in your enterprise](/en/enterprise-cloud@latest/admin/policies/enforcing-policies-for-your-enterprise/enforcing-policies-for-security-settings-in-your-enterprise) in the GitHub Enterprise Cloud documentation.\n", char_interval=CharInterval(start_pos=15358, end_pos=15997), alignment_status=<AlignmentStatus.MATCH_EXACT: 'match_exact'>, extraction_index=13, group_index=12, description=None, attributes={'type': 'textual'})    

Task actions/tutorials/create-actions/create-a-javascript-action.md      
    Extractions:
    Extraction(extraction_class='security_advice', extraction_text='> [!WARNING]\n> When creating workflows and actions, you should always consider whether your code might execute untrusted input from possible attackers. Certain contexts should be treated as untrusted input, as an attacker could insert their own malicious content. For more information, see [Secure use reference](/en/actions/security-guides/security-hardening-for-github-actions#understanding-the-risk-of-script-injections).\n', char_interval=CharInterval(start_pos=1085, end_pos=1086), alignment_status=<AlignmentStatus.MATCH_LESSER: 'match_lesser'>, extraction_index=1, group_index=0, description=None, attributes={'type': 'alert'})    

LangExtract: Saving to result-test.jsonl: 2 docs [00:00, 3227.63 docs/s]
✓ Saved 2 documents to result-test.jsonl
(extraction) root ➜ /workspaces/github-best-pratices/extraction (main) $ 
```
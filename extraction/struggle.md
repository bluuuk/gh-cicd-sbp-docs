/workspaces/github-best-pratices/extraction/gh-docs-2026-02-19/content/code-security/how-tos/report-and-fix-vulnerabilities/fix-reported-vulnerabilities/publishing-a-repository-security-advisory.md

> [!WARNING]
> Whenever possible, you should always add a fix version to a security advisory prior to publishing the advisory. If you don't, the advisory will be published without a fixed version, and Dependabot will alert your users about the issue, without offering any safe version to update to.\n>\n> We recommend you take the following steps in these different situations:\n>\n> * If a fix version is imminently available, and you are able to, wait to disclose the issue when the fix is ready.\n> * If a fix version is in development but not yet available, mention this in the advisory, and edit the advisory later, after publication.\n> * If you are not planning to fix the issue, be clear about it in the advisory so that your users don't contact you to ask when a fix will be made. In this case, it is helpful to include steps users can take to mitigate the issue.\n",

-----

> \[!WARNING]
> Whenever possible, you should always add a fix version to a security advisory prior to publishing the advisory. If you don't, the advisory will be published without a fixed version, and Dependabot will alert your users about the issue, without offering any safe version to update to.
>
> We recommend you take the following steps in these different situations:
>
> * If a fix version is imminently available, and you are able to, wait to disclose the issue when the fix is ready.
> * If a fix version is in development but not yet available, mention this in the advisory, and edit the advisory later, after publication.
> * If you are not planning to fix the issue, be clear about it in the advisory so that your users don't contact you to ask when a fix will be made. In this case, it is helpful to include steps users can take to mitigate the issue.


The only extraction which fails:

            "char_interval": {
                "start_pos": 260,
                "end_pos": 261
            },
            "alignment_status": "match_lesser",
            "extraction_index": 1,
            "group_index": 0,
            "description": null,
            "attributes": {
                "type": "alert"
            }
        }
    ],


-------------

Bug origin: 
    -remark parsing in the preprocessor
    -prompt without the /
Test cases were build on that stuff

Resolution:
    - Just assume \Warning, change prompt
    - Recall that parsing has SIDEEFFECTS!
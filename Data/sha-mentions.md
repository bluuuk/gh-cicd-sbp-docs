If you use a commit SHA when referencing the reusable workflow, you can ensure that everyone who reuses that workflow will always be using the same YAML code. However, if you reference a reusable workflow by a tag or branch, be sure that you can trust that version of the workflow. For more information, see [Secure use reference](/en/actions/security-guides/security-hardening-for-github-actions#reusing-third-party-workflows).
==================================================
Each Git commit receives a calculated SHA value, which is unique and immutable. Your action's users might prefer to rely on a commit's SHA value, as this approach can be more reliable than specifying a tag, which could be deleted or moved. However, this means that users will not receive further updates made to the action. You must use a commit's full SHA value, and not an abbreviated value.
==================================================
Using the commit SHA is the safest option for stability and security. For more information, see [Secure use reference](/en/actions/security-guides/security-hardening-for-github-actions#reusing-third-party-workflows).
==================================================
> \[!NOTE]
> We recommend that you use a SHA value when using third-party actions. However, it's important to note Dependabot will only create Dependabot alerts for vulnerable GitHub Actions that use semantic versioning. For more information, see [Secure use reference](/en/actions/security-guides/security-hardening-for-github-actions#using-third-party-actions) and [About Dependabot alerts](/en/code-security/dependabot/dependabot-alerts/about-dependabot-alerts).
==================================================
If you need more reliable versioning, you should use the SHA value associated with the version of the action. SHAs are immutable and therefore more reliable than tags or branches. However, this approach means you will not automatically receive updates for an action, including important bug fixes and security updates. You must use a commit's full SHA value, and not an abbreviated value. When selecting a SHA, you should verify it is from the action's repository and not a repository fork.
==================================================
Pinning an action to a full-length commit SHA is currently the only way to use an action as an immutable release. Pinning to a particular SHA helps mitigate the risk of a bad actor adding a backdoor to the action's repository, as they would need to generate a SHA-1 collision for a valid Git object payload. When selecting a SHA, you should verify it is from the action's repository and not a repository fork.
==================================================
Although pinning to a commit SHA is the most secure option, specifying a tag is more convenient and is widely used. If you’d like to specify a tag, then be sure that you trust the action's creators. The ‘Verified creator’ badge on GitHub Marketplace is a useful signal, as it indicates that the action was written by a team whose identity has been verified by GitHub.
==================================================
We strongly recommend that you include the version of the action you are using by specifying a Git ref, SHA, or Docker tag number. If you don't specify a version, it could break your workflows or cause unexpected behavior when the action owner publishes an update.

* Using the commit SHA of a released action version is the safest for stability and security.
* Using the specific major action version allows you to receive critical fixes and security patches while still maintaining compatibility. It also assures that your workflow should still work.
* Using the default branch of an action may be convenient, but if someone releases a new major version with a breaking change, your workflow could break.
==================================================
We strongly recommend that you include the version of the action you are using by specifying a Git ref, SHA, or Docker tag. If you don't specify a version, it could break your workflows or cause unexpected behavior when the action owner publishes an update.

* Using the commit SHA of a released action version is the safest for stability and security.
* If the action publishes major version tags, you should expect to receive critical fixes and security patches while still retaining compatibility. Note that this behavior is at the discretion of the action's author.
* Using the default branch of an action may be convenient, but if someone releases a new major version with a breaking change, your workflow could break.
==================================================
Using the commit SHA is the safest option for stability and security. For more information, see [Secure use reference](/en/actions/security-guides/security-hardening-for-github-actions#reusing-third-party-workflows).
==================================================
If you use actions from third parties you should use a version specified by a commit SHA. If the action is revised and you want to use the newer version, you will need to update the SHA. You can specify a version by referencing a tag or a branch, however the action may change without warning. For more information, see [Secure use reference](/en/actions/security-guides/security-hardening-for-github-actions#using-third-party-actions).
==================================================
If you use actions from third parties you should use a version specified by a commit SHA. If the action is revised and you want to use the newer version, you will need to update the SHA. You can specify a version by referencing a tag or a branch, however the action may change without warning. For more information, see [Secure use reference](/en/actions/security-guides/security-hardening-for-github-actions#using-third-party-actions).

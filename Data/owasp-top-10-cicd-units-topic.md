# Insufficient Flow Control Mechanisms

- OWASP/1.1.1: Configure branch protection rules on branches hosting code which is used in production and other sensitive systems.
- OWASP/1.1.2: Where possible, avoid exclusion of user accounts or branches from branch protection rules.
- OWASP/1.1.3: Where user accounts are granted permission to push unreviewed code to a repository, ensure those accounts do not have the permission to trigger the deployment pipelines connected to the repository in question.
- OWASP/1.2.1: Limit the usage of auto-merge rules and ensure that wherever they are in use - they are applicable to the minimal amount of contexts.
- OWASP/1.2.2: Review the code of all auto-merge rules thoroughly to ensure they cannot be bypassed.
- OWASP/1.2.3: Avoid importing 3rd party code in the auto-merge process.
- OWASP/1.3.1: Where applicable, prevent accounts from triggering production build and deployment pipelines without additional approval or review.
- OWASP/1.4.1: Prefer allowing artifacts to flow through the pipeline only in the condition that they were created by a pre-approved CI service account.
- OWASP/1.4.2: Prevent artifacts that have been uploaded by other accounts from flowing through the pipeline without secondary review and approval.
- OWASP/1.5.1: Detect and prevent drifts and inconsistencies between code running in production and its CI/CD origin.
- OWASP/1.5.2: Modify any resource that contains a drift between code running in production and its CI/CD origin.

# Inadequate Identity and Access Management

- OWASP/2.1.1: Conduct a continuous analysis and mapping of all identities across all systems within the engineering ecosystem.
- OWASP/2.1.2: For each identity, map the identity provider, level of permissions granted and level of permissions actually used. Ensure all methods of programmatic access are covered within the analysis.
- OWASP/2.2.1: Remove permissions not necessary for the ongoing work of each identity across the different systems in the environment.
- OWASP/2.3.1: Determine an acceptable period for disabling/removing stale accounts and disable/remove any identity which has surpassed the predetermined period of inactivity.
- OWASP/2.4.1: Avoid creating local user accounts. Instead, create and manage identities using a centralized organization component (IdP).
- OWASP/2.4.2: Whenever local user accounts are in use, ensure that accounts which no longer require access are disabled/removed.
- OWASP/2.4.3: Whenever local user accounts are in use, ensure that security policies around all existing accounts match the organization’s policies.
- OWASP/2.5.1: Continuously map all external collaborators.
- OWASP/2.5.2: Ensure external collaborators' identities are aligned with the principle of least privilege.
- OWASP/2.5.3: Whenever possible, grant permissions with a predetermined expiry date for both human and programmatic accounts of external collaborators.
- OWASP/2.5.4: Disable human and programmatic accounts of external collaborators once the work is done.
- OWASP/2.6.1: Prevent employees from using their personal email addresses, or any address which belongs to a domain not owned and managed by the organization, against the SCM, CI, or any other CI/CD platform.
- OWASP/2.6.2: Continuously monitor for non-domain email addresses across the SCM, CI, or any other CI/CD platform and remove non-compliant users.
- OWASP/2.7.1: Refrain from allowing users to self-register to systems.
- OWASP/2.7.2: Grant user permission to systems on an as-needed basis.
- OWASP/2.8.1: Refrain from granting base permissions in a system to all users, and to large groups where user accounts are automatically assigned to.
- OWASP/2.9.1: Avoid using shared accounts.
- OWASP/2.9.2: Create dedicated accounts for each specific context.
- OWASP/2.9.3: Grant the exact set of permissions required for the context in question.

# Dependency Chain Abuse

- OWASP/3.1.1: Any client pulling code packages should not be allowed to fetch packages directly from the internet or untrusted sources.
- OWASP/3.1.2: Whenever 3rd party packages are pulled from an external repository, ensure all packages are pulled through an internal proxy rather than directly from the internet. This allows deploying additional security controls at the proxy layer, as well as providing investigative capabilities around packages pulled - in case of a security incident.
- OWASP/3.1.3: Where applicable, disallow pulling of packages directly from external repositories.
- OWASP/3.1.4: Configure all clients to pull packages from internal repositories, containing pre-vetted packages.
- OWASP/3.1.5: Establish a mechanism to verify and enforce client configuration to pull packages from internal repositories.
- OWASP/3.2.1: Enable checksum verification for pulled packages.
- OWASP/3.2.2: Enable signature verification for pulled packages.
- OWASP/3.3.1: Avoid configuring clients to pull the latest version of a package.
- OWASP/3.3.2: Prefer configuring clients to pull a pre-vetted version or version ranges.
- OWASP/3.3.3: Use the framework specific techniques to continuously “lock” the package version required in your organization to a stable and secure version.
- OWASP/3.4.1: Ensure all private packages are registered under the organization’s scope.
- OWASP/3.4.2: Ensure all code referencing a private package uses the package’s scope.
- OWASP/3.4.3: Ensure clients are forced to fetch packages that are under your organization’s scope solely from your internal registry.
- OWASP/3.5.1: When installation scripts are being executed as part of the package installation, ensure that a separate context exists for those scripts, which does not have access to secrets and other sensitive resources available in other stages in the build process.
- OWASP/3.6.1: Ensure that internal projects always contain configuration files of package managers (for example .npmrc in NPM) within the code repository of the project, to override any insecure configuration potentially existing on a client fetching the package.
- OWASP/3.7.1: Avoid publishing names of internal projects in public repositories.
- OWASP/3.8.1: As a general rule, given the amount of package managers and configurations in use simultaneously, complete prevention of 3rd party chain abuse is far from trivial. It is therefore recommended to ensure that an appropriate level of focus is placed around detection, monitoring and mitigation to ensure that in case of an incident, it is identified as quickly as possible and has the minimal amount of potential damage.
- OWASP/3.8.2: In the context of 3rd party chain abuse, all relevant systems should be hardened properly according to the guidelines under the “CICD-SEC-7: Insecure System Configuration” risk.

# Poisoned Pipeline Execution (PPE)

- OWASP/4.1.1: Ensure that pipelines running unreviewed code are executed on isolated nodes, not exposed to secrets and sensitive environments.
- OWASP/4.2.1: Evaluate the need for triggering pipelines on public repositories from external contributors.
- OWASP/4.2.2: Where possible, refrain from running pipelines originating from forks.
- OWASP/4.2.3: Consider adding controls such as requiring manual approval for pipeline execution originating from forks.
- OWASP/4.3.1: For sensitive pipelines, for example those that are exposed to secrets, ensure that each branch that is configured to trigger a pipeline in the CI system has a correlating branch protection rule in the SCM.
- OWASP/4.4.1: To prevent the manipulation of the CI configuration file to run malicious code in the pipeline, each CI configuration file must be reviewed before the pipeline runs.
- OWASP/4.4.2: Alternatively to CI configuration file review, the CI configuration file can be managed in a remote branch, separate from the branch containing the code being built in the pipeline.
- OWASP/4.4.3: Configure the remote branch managing the CI configuration file as protected.
- OWASP/4.5.1: Remove permissions granted on the SCM repository from users that do not need them.
- OWASP/4.6.1: Each pipeline should only have access to the credentials it needs to fulfill its purpose.
- OWASP/4.6.2: The credentials used in pipelines should have the minimum required privileges.

# Insufficient PBAC (Pipeline-Based Access Controls)

- OWASP/5.1.1: Do not use a shared node for pipelines with different levels of sensitivity (i.e., shared nodes should be used only for pipelines with identical levels of confidentiality).
- OWASP/5.1.2: Do not use a shared node for pipelines that require access to different resources.
- OWASP/5.2.1: Ensure secrets that are used in CI/CD systems are scoped in a manner that allows each pipeline and step to have access to only the secrets it requires.
- OWASP/5.3.1: Revert the execution node to its pristine state after each pipeline execution.
- OWASP/5.4.1: Ensure the OS user running the pipeline job has been granted OS permissions on the execution node according to the principle of least privilege.
- OWASP/5.5.1: CI and CD pipeline jobs should have limited permissions on the controller node.
- OWASP/5.5.2: Where applicable, run pipeline jobs on a separate, dedicated node.
- OWASP/5.6.1: Ensure the execution node is appropriately patched.
- OWASP/5.7.1: Ensure network segmentation in the environment the job is running on is configured to allow the execution node to access only the resources it requires within the network.
- OWASP/5.7.2: Where possible, refrain from granting unlimited access towards the internet to build nodes.
- OWASP/5.8.1: When installation scripts are being executed as part of the package installation, ensure that a separate context exists for those scripts, which does not have access to secrets and other sensitive resources available in other stages in the build process.

# Insufficient Credential Hygiene

- OWASP/6.1.1: Establish procedures to continuously map credentials found across the different systems in the engineering ecosystem - from code to deployment.
- OWASP/6.1.2: Ensure each set of credentials follows the principle of least privilege and has been granted the exact set of permission needed by the service using it.
- OWASP/6.2.1: Avoid sharing the same set of credentials across multiple contexts. This increases the complexity of achieving the principle of least privilege as well as having a negative effect on accountability.
- OWASP/6.3.1: Prefer using temporary credentials over static credentials.
- OWASP/6.3.2: In case static credentials need to be in use - establish a procedure to periodically rotate all static credentials.
- OWASP/6.3.3: Detect stale static credentials.
- OWASP/6.4.1: Configure the usage of credentials to be limited to predetermined conditions (like scoping to a specific source IP or identity) to ensure that even in case of compromise, exfiltrated credentials cannot be used outside your environment.
- OWASP/6.5.1: Detect secrets pushed to and stored on code repositories.
- OWASP/6.5.2: Use controls such as an IDE plugin to identify secrets used in the local changes.
- OWASP/6.5.3: Use controls such as automatic scanning upon each code push to detect secrets.
- OWASP/6.5.4: Use controls such as periodical scans on the repository and its past commits to detect secrets.
- OWASP/6.6.1: Ensure secrets that are used in CI/CD systems are scoped in a manner that allows each pipeline and step to have access to only the secrets it requires.
- OWASP/6.7.1: Use built-in vendor options or 3rd party tools to prevent secrets from being printed to console outputs of future builds.
- OWASP/6.7.2: Ensure all existing console outputs of builds do not contain secrets.
- OWASP/6.8.1: Verify that secrets are removed from any type of artifact, such as from layers of container images, binaries, or Helm charts.

# Insecure System Configuration

- OWASP/7.1.1: Maintain an inventory of systems and versions in use, including mapping of a designated owner for each system.
- OWASP/7.1.2: Continuously check for known vulnerabilities in all systems and versions in use.
- OWASP/7.1.3: If a security patch is available, update the vulnerable component.
- OWASP/7.1.4: If no security patch is available, consider removing the component / system.
- OWASP/7.1.5: If no security patch is available, reduce the potential impact of exploiting the vulnerability by restricting access to the system.
- OWASP/7.1.6: If no security patch is available, reduce the potential impact of exploiting the vulnerability by restricting the system’s ability to perform sensitive operations.
- OWASP/7.2.1: Ensure network access to the systems is aligned with the principle of least access.
- OWASP/7.3.1: Establish a process to periodically review all system configurations for any setting that can have an effect on the security posture of the system and ensure all settings are optimal.
- OWASP/7.4.1: Ensure permissions to the pipeline execution nodes are granted according to the principle of least privilege.
- OWASP/7.4.2: A common misconfiguration regarding permissions to the pipeline execution nodes is around granting debug permissions on execution nodes to engineers. While in many organizations this is a common practice, it is imperative to take into consideration that any user with the ability to access the execution node in debug mode may expose all secrets while they are loaded into memory and use the node’s identity - effectively granting elevated permissions to any engineer with this permission.

# Ungoverned Usage of 3rd Party Services

- OWASP/8.1.1: Establish vetting procedures to ensure 3rd parties granted access to resources anywhere across the engineering ecosystem are approved prior to being granted access to the environment.
- OWASP/8.1.2: Establish vetting procedures to ensure that the level of permission granted to 3rd parties accessing resources anywhere across the engineering ecosystem is aligned with the principle of least privilege.
- OWASP/8.2.1: Maintain continuous visibility over all 3rd parties integrated to CI/CD systems to make sure all methods of integration for each system are covered (including marketplace apps, plugins, OAuth applications, programmatic access tokens, etc.).
- OWASP/8.2.2: Maintain continuous visibility over all 3rd parties integrated to CI/CD systems with regards to the level of permission granted to the 3rd party.
- OWASP/8.2.3: Maintain continuous visibility over all 3rd parties integrated to CI/CD systems with regards to the level of permission actually in use by the 3rd party.
- OWASP/8.3.1: Ensure each 3rd party is limited and scoped to the specific resources it requires access to.
- OWASP/8.3.2: Remove unused and/or redundant permissions granted to 3rd parties.
- OWASP/8.3.3: 3rd parties which are integrated as part of the Build process should run inside a scoped context with limited access to secrets and code, and with strict ingress and egress filters.
- OWASP/8.4.1: Periodically review all 3rd parties integrated and remove those no longer in use.

# Improper Artifact Integrity Validation

- OWASP/9.1.1: Implement processes and technologies to validate the integrity of resources all the way from development to production.
- OWASP/9.1.2: When a resource is generated, the process to validate the integrity of resources will include signing that resource using an external resource signing infrastructure.
- OWASP/9.1.3: Prior to consuming the resource in subsequent steps down the pipeline, the resource’s integrity should be validated against the signing authority.
- OWASP/9.1.4: Use SCM solutions that provide the ability to sign commits using a unique key for each contributor. This measure can then be leveraged to prevent unsigned commits from flowing down the pipeline.
- OWASP/9.1.5: Use tools for signing and verification of code and artifacts to provide a way to prevent unverified software from being delivered down the pipeline. Examples for such projects are in-toto, SLSA, and Sigstore, all part of the Linux Foundation.
- OWASP/9.1.6: Consider measures aimed at detecting configuration drifts (e.g. resources in cloud environments which aren’t managed using a signed IAC template), potentially indicative of resources that were deployed by an untrusted source or process.
- OWASP/9.2.1: For 3rd party resources fetched from build/deploy pipelines (such as scripts imported and executed as part of the build process), calculate the hash of the resource and cross reference against the official published hash of the resource provider.

# Insufficient Logging and Visibility

- OWASP/10.1.1: Strong visibility capabilities cannot be achieved without an intimate level of familiarity with all the different systems involved in potential threats. A potential breach may involve any of the systems which take part in the CI/CD processes, including SCM, CI, Artifact repositories, package management software, container registries, CD, and orchestration engines (e.g. K8s). Identify and build an inventory of all the systems in use within the organization, containing every instance of these systems (specifically relevant for self-managed systems e.g. Jenkins).
- OWASP/10.2.1: Ensure that all relevant logs are enabled for all systems in use within the organization, as this is not the default state in the different systems.
- OWASP/10.2.2: Visibility of systems in use within the organization should be optimized around both human access as well as programmatic access through all the various measures it is allowed.
- OWASP/10.2.3: It is important to place an equal level of emphasis on identifying all relevant audit log sources, as well as the applicative log sources.
- OWASP/10.3.1: Ship logs to a centralized location (e.g. SIEM), to support aggregation and correlation of logs between different systems for detection and investigation.
- OWASP/10.4.1: Create alerts to detect anomalies and potential malicious activity, both in each system on its own and anomalies in the code shipping process, which involves multiple systems and requires deeper knowledge in the internal build and deployments processes.


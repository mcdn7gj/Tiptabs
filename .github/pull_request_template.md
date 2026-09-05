## Overview

<!--
Write 1-3 sentences describing the outcome of this pull request and why it is
needed. Lead with the user, operational, or maintainer value. Keep this high
level; put implementation details in Changes below.
-->

## Changes

<!--
List each modified file or focused area and explain what changed and why.
Use concrete, reviewer-friendly language. Prefer one bullet per file or area,
for example: `Dockerfile`: upgraded the base image to improve compatibility.
Do not paste a commit log or list files without explaining their purpose.
-->

The following files were modified in these changes:
- `path/to/file`: describe the change and its purpose.

## Testing

<!--
Document the exact commands run locally or in CI. Include the important
expected result for each command, especially for endpoints, containers, or
deployment changes. If a check was not needed, explain why. Write commands
and results so another maintainer can reproduce the verification.
-->

To verify these changes, the following commands were run locally:

```text
# Command
# Expected result
```

<!-- For Docker, deployment, or CI changes, also verify the checks below. -->

- [ ] Docker image builds successfully
- [ ] Container health check passes at `/health`

<!--
Include screenshots only when they add useful evidence, such as a UI result,
container output, or CI run. Add a short description for each screenshot.
-->

## Cleanup

<!--
For temporary containers, images, services, or other local resources, list the
cleanup commands used. Write `None` when no cleanup is required.
-->

```text
# Cleanup commands, or None
```

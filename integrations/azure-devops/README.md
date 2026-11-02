# Mandrel Spec Validation for Azure DevOps

Use this Azure DevOps step template to validate Mandrel specifications in Azure Pipelines. The template invokes the Mandrel CLI container via Docker on Linux pipeline agents to enforce schema correctness and governance constraints.

## Usage

Reference this step template in your `azure-pipelines.yml`:

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  - checkout: self

  - template: integrations/azure-devops/validate-mandrel-spec.yml@mandrelTemplates
    parameters:
      specPath: 'mandrel-spec.yaml'
      strict: true
```

If copying the template file directly into your repository (for example at `.azure-pipelines/steps/validate-mandrel-spec.yml`):

```yaml
steps:
  - template: .azure-pipelines/steps/validate-mandrel-spec.yml
    parameters:
      specPath: 'mandrel-spec.yaml'
      strict: true
```

## Parameters

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `specPath` | string | Path to the specification relative to repository root | `mandrel-spec.yaml` |
| `imageTag` | string | CLI image tag to pull and execute | `latest` |
| `strict` | boolean | Escalate validation warnings to fatal errors | `false` |
| `allowUnclaimedExtensions` | boolean | Allow undeclared extension fields | `false` |
| `extraArgs` | string | Additional flags to pass directly to `mandrel validate` | `''` |

## Local Emulation

To test this step locally using Podman before committing:

```bash
podman run --rm \
  -v "$(pwd):/workspace:ro" \
  -w /workspace \
  registry.gitlab.com/the-mandrel-project/mandrel-containers/cli:latest \
  validate mandrel-spec.yaml
```

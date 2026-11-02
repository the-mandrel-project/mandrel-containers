# Mandrel Spec Validation for GitHub Actions

Use this GitHub Action to validate Mandrel specifications directly in your GitHub workflows. The action runs the zero-dependency Mandrel CLI container to verify YAML schemas, required governance constraints, and core protocol invariants.

## Usage

Add the step to your workflow file (for example, `.github/workflows/validate.yml`):

```yaml
name: Validate Specifications

on:
  push:
    branches: [main]
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Validate Mandrel Spec
        uses: the-mandrel-project/mandrel-containers/integrations/github@v0.0.1
        with:
          spec-path: "mandrel-spec.yaml"
          strict: "true"
```

## Inputs

| Name | Description | Default |
| --- | --- | --- |
| `spec-path` | Path to the specification file relative to repository root | `mandrel-spec.yaml` |
| `image-tag` | Tag of `registry.gitlab.com/the-mandrel-project/mandrel-containers/cli` | `latest` |
| `strict` | Treat warnings as fatal errors (`true` or `false`) | `false` |
| `allow-unclaimed-extensions` | Permit unclaimed extension keys (`true` or `false`) | `false` |

## Local Emulation

To test this action locally using Podman before pushing:

```bash
podman run --rm \
  -v "$(pwd):/workspace:ro" \
  -w /workspace \
  registry.gitlab.com/the-mandrel-project/mandrel-containers/cli:latest \
  validate mandrel-spec.yaml
```

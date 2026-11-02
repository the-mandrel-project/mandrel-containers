# Mandrel Spec Validation for Google Cloud Build

Use this configuration to validate Mandrel specifications in Google Cloud Build pipelines. Because Cloud Build steps execute container images directly and mount repository sources at `/workspace`, the Mandrel CLI container runs natively with zero runtime dependencies.

## Usage

Include this step in your `cloudbuild.yaml`:

```yaml
steps:
  # Validate Mandrel specification before building or packaging
  - id: 'validate-mandrel-spec'
    name: 'registry.gitlab.com/the-mandrel-project/mandrel-containers/cli:latest'
    args:
      - 'validate'
      - '--strict'
      - 'mandrel-spec.yaml'
```

Alternatively, invoke the standalone configuration file directly with `gcloud builds submit`:

```bash
gcloud builds submit \
  --config=integrations/cloudbuild/validate-mandrel-spec.yaml \
  --substitutions=_MANDREL_SPEC_PATH=mandrel-spec.yaml,_MANDREL_CLI_TAG=latest
```

## Substitutions

| Name | Description | Default |
| --- | --- | --- |
| `_MANDREL_SPEC_PATH` | Path to the specification file relative to repository root | `mandrel-spec.yaml` |
| `_MANDREL_CLI_TAG` | Image tag of the Mandrel CLI container to execute | `latest` |

## Local Emulation

Cloud Build steps execute containers with the repository mounted at `/workspace`. Test this locally with Podman:

```bash
podman run --rm \
  -v "$(pwd):/workspace:ro" \
  -w /workspace \
  registry.gitlab.com/the-mandrel-project/mandrel-containers/cli:latest \
  validate mandrel-spec.yaml
```

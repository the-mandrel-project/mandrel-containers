# Mandrel Spec Validation for GitLab CI

Use this template to validate Mandrel specifications in GitLab CI pipelines. The component runs within GitLab CI/CD pipelines to ensure specifications comply with official schemas and runtime policies before merging or publishing.

## Usage

### CI/CD Catalog Component

Add the component to your `.gitlab-ci.yml`:

```yaml
stages:
  - lint
  - build

include:
  - component: $CI_SERVER_FQDN/the-mandrel-project/mandrel-ci/validate-spec@v2.4.0
    inputs:
      stage: lint
      spec_path: "mandrel-spec.yaml"
      strict: true
```

### Local File Include

If including the template file directly from a local repository:

```yaml
stages:
  - lint

include:
  - local: integrations/gitlab/validate-mandrel-spec.yml
    inputs:
      stage: lint
      spec_path: "mandrel-spec.yaml"
```

## Inputs

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `stage` | string | Pipeline stage in which to run spec validation | `lint` |
| `spec_path` | string | Relative path to the specification file | `mandrel-spec.yaml` |
| `image_tag` | string | Container tag of the Mandrel CLI image | `latest` |
| `strict` | boolean | Escalate validation warnings to fatal errors | `false` |
| `allow_unclaimed_extensions` | boolean | Allow undeclared extension fields | `false` |

## Local Emulation

To test this validation job locally using Podman before pushing:

```bash
podman run --rm \
  -v "$(pwd):/workspace:ro" \
  -w /workspace \
  registry.gitlab.com/the-mandrel-project/mandrel-containers/cli:latest \
  validate mandrel-spec.yaml
```

## Exit Codes and Pipeline Behavior

The Mandrel CLI returns deterministic exit codes to differentiate specification violations from operational errors:

| Exit Code | Constant | Meaning | Pipeline Behavior |
| :--- | :--- | :--- | :--- |
| `0` | `ExitSuccess` | Specification passed validation cleanly | Job succeeds |
| `1` | `ExitGeneral` | Operational failure (missing file, invalid flag syntax) | Job fails (infrastructure error) |
| `2` | `ExitValidation` | Specification violated schema or governance constraints | Job fails (spec invalid) |
| `3` | `ExitAuth` | Token missing or authentication failure | Job fails (auth error) |
| `4` | `ExitPlugin` | Plugin execution failed or crashed | Job fails (plugin error) |

Pipelines running in advisory mode can soft-fail on specification errors while still failing hard on operational problems:

```yaml
validate-mandrel-spec:
  allow_failure:
    exit_codes: [2]
```


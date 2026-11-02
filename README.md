# Mandrel Containers

Official container images for the Mandrel ecosystem, providing hardened, zero-dependency distributions for CI/CD pipelines, local developer toolchains, and Kubernetes execution.

## Container Inventory

| Image | Registry Path | Description | Base |
| :--- | :--- | :--- | :--- |
| **Mandrel CLI** | `registry.gitlab.com/the-mandrel-project/mandrel-containers/cli` | Batteries-included Mandrel CLI bundled with official plugins (`mandrel-generator-kong`). | `distroless/static-debian12:nonroot` |
| **Mandrel Collet** | `registry.gitlab.com/the-mandrel-project/mandrel-collet` | High-performance enforcement sidecar for autonomous agent governance. | `distroless/static-debian12:nonroot` |

---

## Mandrel CLI Container

The CLI container packages `mandrel-cli` alongside official generator and validator plugins. It is compiled statically with CGO disabled and packaged into distroless static Debian 12, running as non-root (`uid 65532`).

### Quick Start

Pull the image:

```bash
docker pull registry.gitlab.com/the-mandrel-project/mandrel-containers/cli:latest
```

Verify installed plugins:

```bash
docker run --rm registry.gitlab.com/the-mandrel-project/mandrel-containers/cli plugins list
```

Output:
```text
NAME                       KIND       VERSION  COMPAT  PATH
mandrel.io/kong-generator  generator  0.1.0    ^1.0.0  /usr/local/bin/mandrel-generator-kong
```

### Validating a Mandrel Spec

Mount your local specification directory into `/workspace`:

```bash
docker run --rm -v $(pwd):/workspace:ro \
  registry.gitlab.com/the-mandrel-project/mandrel-containers/cli \
  validate finance-agent.yaml
```

### Generating Gateway Artifacts (Kong)

Generate Kong Gateway plugins and mesh permissions from a Realized Spec:

```bash
docker run --rm -v $(pwd):/workspace \
  registry.gitlab.com/the-mandrel-project/mandrel-containers/cli \
  generate finance-agent.realized.yaml ./output
```

---

## Building Locally

Build the container image using Podman or Docker:

```bash
podman build -t mandrel-cli:local .
```

To pin specific git references during build:

```bash
podman build \
  --build-arg CLI_REF=main \
  --build-arg KONG_REF=main \
  -t mandrel-cli:local .
```

---

## Security & Compliance

* **Rootless**: Runs under `nonroot` (`uid 65532:gid 65532`).
* **Zero System Dependencies**: Contains no shell, package managers, or dynamic linkers.
* **Minimal Attack Surface**: Uses Google Distroless static base image containing only root CA certificates.

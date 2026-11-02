# Rules of Engagement for AI Agents (mandrel-containers)

This document defines the mandatory rules and engineering standards for all agents (AI or human) contributing to the `mandrel-containers` repository.

## 1. Core Principles
* **Zero-Dependency Mandate**: All container images in this repository must use minimal, unprivileged bases (`gcr.io/distroless/static-debian12:nonroot` or `scratch`). Binaries must be statically compiled with `CGO_ENABLED=0` and stripped of debugging symbols (`-ldflags="-s -w"`). Never introduce full Linux distributions (Ubuntu, Debian glibc, standard Alpine) into production runtime containers.
* **Non-Root Execution**: Container runtimes must run under unprivileged user identities (e.g., `nonroot:nonroot`, UID 65532). Never run as root.
* **Fail-Closed Governance**: If an image build or plugin discovery check fails, the pipeline must terminate immediately. Never publish an image with missing or broken plugins.
* **Human-in-the-Loop (HITL)**: All git check-in operations require explicit human approval prior to execution.
* **American English Standard**: Use American English exclusively across all documentation, comments, Dockerfiles, and commit messages (e.g., *behavior*, *authorize*, *center*, *catalog*, *defense*).
* **DCO Sign-off**: Every git commit must include the `-s` (`Signed-off-by`) flag adhering to the Developer Certificate of Origin.

## 2. Verification Standards
* Before committing changes or publishing images, all containers must pass local and CI verification:
  1. Entrypoint execution test (`mandrel --help`).
  2. Plugin discovery test (`mandrel plugins list` asserting that all bundled plugins are discovered).
  3. Spec validation test against a specimen specification.
* Never publish a container tag until test execution confirms stability.

## 3. Versioning Standards
* All image tags must adhere to Semantic Versioning (SemVer) (e.g., `v0.1.0`).
* Increment the patch version on every push to the default branch.
* Tag both specific SemVer releases (`$VERSION`), short commit SHAs (`$CI_COMMIT_SHORT_SHA`), and `:latest`.

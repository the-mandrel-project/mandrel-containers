#!/usr/bin/env python3
"""Integration test runner for Mandrel CI templates and container validation.

Validates the structure and execution contracts of Mandrel CI templates across:
- GitHub Actions
- Azure DevOps Pipelines
- Google Cloud Build
- GitLab CI/CD Components

Supports syntax linting and runtime execution emulation using Podman or Docker.
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys
import yaml

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
POSITIVE_FIXTURE = "tests/fixtures/positive/valid-spec.yaml"
NEGATIVE_FIXTURE = "tests/fixtures/negative/invalid-spec.yaml"


def lint_gitlab_component(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        docs = list(yaml.safe_load_all(f))
    if len(docs) != 2:
        raise ValueError(f"Expected 2 YAML documents (spec and config), found {len(docs)}")
    spec, config = docs
    if not isinstance(spec, dict) or "spec" not in spec or "inputs" not in spec["spec"]:
        raise ValueError("Missing 'spec.inputs' definition")
    for name, cfg in spec["spec"]["inputs"].items():
        if not isinstance(cfg, dict) or not cfg.get("description"):
            raise ValueError(f"Input '{name}' lacks description")
    jobs = [k for k in config if not k.startswith(".") and k not in ("variables", "stages", "default")]
    if not jobs:
        raise ValueError("Component declares no executable jobs")


def lint_github_action(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("Root must be a YAML mapping")
    for key in ("name", "description", "runs", "inputs"):
        if key not in data:
            raise ValueError(f"Missing required top-level key: {key}")
    if data["runs"].get("using") != "composite":
        raise ValueError("Action must use 'composite' execution")
    if not data["runs"].get("steps"):
        raise ValueError("Action contains no execution steps")


def lint_azure_devops_template(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("Root must be a YAML mapping")
    if "parameters" not in data or not isinstance(data["parameters"], list):
        raise ValueError("Azure DevOps template must declare a parameters list")
    if "steps" not in data or not isinstance(data["steps"], list) or not data["steps"]:
        raise ValueError("Azure DevOps template must declare at least one step")


def lint_cloudbuild_config(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("Root must be a YAML mapping")
    if "steps" not in data or not isinstance(data["steps"], list) or not data["steps"]:
        raise ValueError("Cloud Build config must declare at least one step")
    for i, step in enumerate(data["steps"]):
        if "name" not in step:
            raise ValueError(f"Step {i} missing 'name' attribute")


def run_lint_suite() -> bool:
    print("=== Phase 1: Linting CI Integration Templates ===")
    linters = {
        "integrations/github/action.yml": lint_github_action,
        "integrations/azure-devops/validate-mandrel-spec.yml": lint_azure_devops_template,
        "integrations/cloudbuild/validate-mandrel-spec.yaml": lint_cloudbuild_config,
        "integrations/gitlab/validate-mandrel-spec.yml": lint_gitlab_component,
    }

    all_ok = True
    for rel_path, linter in linters.items():
        abs_path = os.path.join(REPO_ROOT, rel_path)
        if not os.path.exists(abs_path):
            print(f"[FAIL] Missing template: {rel_path}")
            all_ok = False
            continue
        try:
            linter(abs_path)
            print(f"[PASS] Lint: {rel_path}")
        except Exception as exc:
            print(f"[FAIL] Lint: {rel_path}: {exc}")
            all_ok = False

    # Check fixtures exist and parse as YAML
    for fixture in (POSITIVE_FIXTURE, NEGATIVE_FIXTURE):
        abs_fixture = os.path.join(REPO_ROOT, fixture)
        try:
            with open(abs_fixture, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict) or data.get("kind") != "MandrelSpec":
                raise ValueError("Must declare kind: MandrelSpec")
            print(f"[PASS] Fixture syntax: {fixture}")
        except Exception as exc:
            print(f"[FAIL] Fixture syntax: {fixture}: {exc}")
            all_ok = False

    return all_ok


def detect_container_runtime() -> str:
    # Prioritize podman as configured, fall back to docker
    for cmd in ("podman", "docker"):
        if shutil.which(cmd):
            return cmd
    return ""


def run_command(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return proc.returncode, proc.stdout


def run_emulation_suite(engine: str, image: str) -> bool:
    print(f"\n=== Phase 2: Runtime Contract Emulation ({engine}) ===")
    print(f"Target Image: {image}")

    tests = [
        {
            "platform": "GitHub Actions",
            "fixture": POSITIVE_FIXTURE,
            "args": ["validate", POSITIVE_FIXTURE],
            "expected_exit": 0,
        },
        {
            "platform": "GitHub Actions",
            "fixture": NEGATIVE_FIXTURE,
            "args": ["validate", "--strict", NEGATIVE_FIXTURE],
            "expected_exit": 2,
        },
        {
            "platform": "Azure DevOps",
            "fixture": POSITIVE_FIXTURE,
            "args": ["validate", POSITIVE_FIXTURE],
            "expected_exit": 0,
        },
        {
            "platform": "Azure DevOps",
            "fixture": NEGATIVE_FIXTURE,
            "args": ["validate", NEGATIVE_FIXTURE],
            "expected_exit": 2,
        },
        {
            "platform": "Google Cloud Build",
            "fixture": POSITIVE_FIXTURE,
            "args": ["validate", POSITIVE_FIXTURE],
            "expected_exit": 0,
        },
        {
            "platform": "Google Cloud Build",
            "fixture": NEGATIVE_FIXTURE,
            "args": ["validate", NEGATIVE_FIXTURE],
            "expected_exit": 2,
        },
        {
            "platform": "GitLab CI",
            "fixture": POSITIVE_FIXTURE,
            "args": ["validate", POSITIVE_FIXTURE],
            "expected_exit": 0,
        },
        {
            "platform": "GitLab CI",
            "fixture": NEGATIVE_FIXTURE,
            "args": ["validate", NEGATIVE_FIXTURE],
            "expected_exit": 2,
        },
    ]

    all_ok = True
    for test in tests:
        platform = test["platform"]
        fixture = test["fixture"]
        cmd = [
            engine,
            "run",
            "--rm",
            "-v",
            f"{REPO_ROOT}:/workspace:ro",
            "-w",
            "/workspace",
            image,
        ] + test["args"]

        ret, out = run_command(cmd)
        expected = test.get("expected_exit", 0)
        success = (ret == expected)

        status_tag = "[PASS]" if success else "[FAIL]"
        case_type = "positive" if expected == 0 else f"negative (exit {expected})"
        print(f"{status_tag} {platform} ({case_type}) -> exit code {ret}")

        if not success:
            all_ok = False
            print(f"       Expected exit {expected}, got {ret}")
            print(f"       Output:\n{out.strip()}\n")

    return all_ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Test CI templates and container validation.")
    parser.add_argument("--lint-only", action="store_true", help="Only run template linting without container tests")
    parser.add_argument(
        "--image",
        default="registry.gitlab.com/the-mandrel-project/mandrel-containers/cli:latest",
        help="Container image to test against",
    )
    args = parser.parse_args()

    lint_passed = run_lint_suite()
    if not lint_passed:
        print("\nLint checks failed.")
        return 1

    if args.lint_only:
        print("\nLint checks succeeded. Skipping runtime emulation (--lint-only).")
        return 0

    engine = detect_container_runtime()
    if not engine:
        print("\nNo container runtime (podman or docker) detected. Skipping runtime emulation.")
        return 1

    emulation_passed = run_emulation_suite(engine, args.image)
    if not emulation_passed:
        print("\nRuntime emulation tests failed.")
        return 1

    print("\nAll integration checks and contract emulations passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

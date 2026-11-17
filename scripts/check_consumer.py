"""Exercise a pinned real consumer against candidate artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from verify_shared_distribution import verify


def run(args, cwd, env=None):
    subprocess.run(args, cwd=cwd, env=env, check=True)


def candidate_manifest(root, metadata, wheel, tarball, operations):
    """Point the consumer's real operations fetcher at the checked candidate."""
    path = root / "shared-libraries.json"
    manifest = json.loads(path.read_text())
    manifest["source_commit"] = metadata["source_commit"]
    for key, version, artifact in [
        ("core", metadata["core_version"], wheel),
        ("core_ui", metadata["core_ui_version"], tarball),
        ("operations", metadata["operations_version"], operations),
    ]:
        manifest[key] = {
            "version": version,
            "url": artifact.resolve().as_uri(),
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        }
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def check_operations(python, root, extracted):
    # Use the consumer's interpreter/dependencies, never the platform's app sources.
    code = """
import importlib.util, os, pathlib, runpy, sys
from importlib.metadata import distribution
import app
assert pathlib.Path(app.__file__).resolve().is_relative_to(pathlib.Path(sys.prefix).resolve())
assert distribution('copilot-core').version == sys.argv[3]
spec = importlib.util.spec_from_file_location('artifact_verify', sys.argv[1])
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
with helper.disposable_database(os.environ['OPERATIONS_TEST_DATABASE_URL']) as url:
    os.environ['DATABASE_URL'] = url
    os.environ['DOMAIN_PLUGINS'] = ''
    os.environ['REDIS_URL'] = ''
    os.environ['GRAPH_RAG_ENABLED'] = 'false'
    os.environ['CHECKPOINTING_ENABLED'] = 'false'
    os.environ['AMQP_ENABLED'] = 'false'
    from alembic import command
    from alembic.config import Config
    config = Config(str(pathlib.Path(sys.argv[2]) / 'alembic.ini'))
    command.upgrade(config, 'head')
    command.check(config)
    os.chdir(sys.argv[2])
    sys.argv = [str(pathlib.Path.cwd() / 'scripts/validate_dashboards.py')]
    runpy.run_path(sys.argv[0], run_name='__main__')
"""
    version = json.loads((root / "shared-libraries.json").read_text())["core"]["version"]
    run(
        [
            str(python),
            "-I",
            "-c",
            code,
            str(Path(__file__).with_name("verify_shared_distribution.py").resolve()),
            str(extracted),
            version,
        ],
        extracted,
    )


def check(artifacts, repository, commit, kind, postgres=False, report=None):
    metadata = json.loads((artifacts / "distribution.json").read_text())
    if postgres and not os.environ.get("OPERATIONS_TEST_DATABASE_URL"):
        raise ValueError("--postgres requires OPERATIONS_TEST_DATABASE_URL")
    wheel, operations = verify(artifacts)
    (tarball,) = artifacts.glob("copilot-core-ui-*.tgz")
    with tempfile.TemporaryDirectory(prefix="platform-consumer-") as tmp:
        root = Path(tmp) / "consumer"
        run(["git", "clone", "--no-checkout", repository, str(root)], Path(tmp))
        run(["git", "checkout", "--detach", commit], root)
        if kind == "iic":
            run(["python3", "scripts/quality_gate.py"], root)
        candidate = candidate_manifest(root, metadata, wheel, tarball, operations)
        project = root / "pyproject.toml"
        text = project.read_text()
        text = re.sub(
            r'copilot-core(\[[^\]]+\])?==[^"]+',
            lambda m: "copilot-core" + (m[1] or "") + "==" + metadata["core_version"],
            text,
        )
        text = re.sub(
            r"^copilot-core\s*=.*$",
            "copilot-core = { path = " + json.dumps(str(wheel.resolve())) + " }",
            text,
            flags=re.MULTILINE,
        )
        project.write_text(text)
        ui = root / "frontend/package.json"
        package = json.loads(ui.read_text())
        package["dependencies"]["@copilot/core-ui"] = "file:" + str(tarball.resolve())
        ui.write_text(json.dumps(package, indent=2) + "\n")
        run(["uv", "sync", "--python", "3.12", "--no-install-project"], root)
        run(["npm", "install", "--ignore-scripts"], root / "frontend")
        for command in ["lint", "typecheck", "build"]:
            run(["npm", "run", command], root / "frontend")
        env = {**os.environ, "DFE_BUILD_REQUIRE_UI": "1", "IIC_BUILD_REQUIRE_UI": "1"}
        run(["uv", "build", "--wheel", "--no-sources", "--out-dir", "dist"], root, env)
        python = root / ".venv/bin/python"
        (product,) = (root / "dist").glob("*.whl")
        run(["uv", "pip", "install", "--python", str(python), "--no-deps", str(product)], root)
        script = "scripts/quality_gate.py" if kind == "iic" else "scripts/verify_install.py"
        if kind == "fisc":
            run([str(python), "-I", script], root)
        extracted = Path(tmp) / "operations"
        run([str(python), "-I", "scripts/fetch_operations.py", str(extracted)], root)
        if postgres:
            check_operations(python, root, extracted)
        run(
            [
                str(python),
                "-I",
                "-m",
                "pytest",
                "-c",
                "pyproject.toml",
                "-o",
                "pythonpath=",
                "tests",
                "-q",
                "--tb=short",
            ],
            root,
        )
        result = {
            "consumer": kind,
            "consumer_commit": commit,
            "platform_commit": metadata["source_commit"],
            "components": candidate,
            "operations_postgres": "passed" if postgres else "not-run",
            "ui_and_product_tests": "passed",
        }
        if report:
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(json.dumps(result, indent=2) + "\n")
        print(
            kind,
            commit,
            "passed with",
            metadata["core_version"],
            metadata["core_ui_version"],
            metadata["operations_version"],
        )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--artifacts", type=Path, required=True)
    p.add_argument("--postgres", action="store_true")
    p.add_argument("--report", type=Path)
    p.add_argument("--repository")
    p.add_argument("--manifest", type=Path)
    p.add_argument("--commit")
    p.add_argument("--kind", choices=["iic", "fisc"], required=True)
    args = p.parse_args()
    if args.manifest:
        consumer = json.loads(args.manifest.read_text())[args.kind]
        args.repository, args.commit = consumer["repository"], consumer["commit"]
    if not args.repository or not args.commit:
        p.error("Provide --manifest or --repository and --commit")
    check(
        args.artifacts.resolve(),
        args.repository,
        args.commit,
        args.kind,
        postgres=args.postgres,
        report=args.report,
    )

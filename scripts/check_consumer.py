"""Exercise a pinned real consumer against candidate artifacts."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path


def run(args, cwd, env=None):
    subprocess.run(args, cwd=cwd, env=env, check=True)


def check(artifacts, repository, commit, kind):
    metadata = json.loads((artifacts / "distribution.json").read_text())
    (wheel,) = artifacts.glob("copilot_core-*.whl")
    (tarball,) = artifacts.glob("copilot-core-ui-*.tgz")
    with tempfile.TemporaryDirectory(prefix="platform-consumer-") as tmp:
        root = Path(tmp) / "consumer"
        run(["git", "clone", "--no-checkout", repository, str(root)], Path(tmp))
        run(["git", "checkout", "--detach", commit], root)
        if kind == "iic":
            run(["python3", "scripts/quality_gate.py"], root)
        if kind == "iic":
            run(["python3", "scripts/quality_gate.py"], root)
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
        print(kind, commit, "passed with", metadata["core_version"], metadata["core_ui_version"])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--artifacts", type=Path, required=True)
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
    check(args.artifacts.resolve(), args.repository, args.commit, args.kind)

"""Promote one independently versioned component from a successful main CI run."""

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


def gh(*args):
    return subprocess.check_output(["gh", *args], text=True).strip()


def publish(repo, run_id, component):
    run = json.loads(gh("api", f"repos/{repo}/actions/runs/{run_id}"))
    assert run["name"] == "Platform CI" and run["conclusion"] == "success"
    assert run["head_branch"] == "main" and run["event"] in {"push", "workflow_dispatch"}
    with tempfile.TemporaryDirectory(prefix="platform-release-") as tmp:
        root = Path(tmp)
        subprocess.run(
            ["gh", "run", "download", str(run_id), "--repo", repo, "--dir", str(root / "input")],
            check=True,
        )
        (metadata_path,) = (root / "input").rglob("distribution.json")
        folder = metadata_path.parent
        metadata = json.loads(metadata_path.read_text())
        assert metadata["source_dirty"] is False and metadata["source_commit"] == run["head_sha"]
        versions = {
            "core": metadata["core_version"],
            "core-ui": metadata["core_ui_version"],
            "operations": metadata["operations_version"],
        }
        patterns = {
            "core": ["copilot_core-*.whl", "copilot_core-*.tar.gz"],
            "core-ui": ["copilot-core-ui-*.tgz"],
            "operations": ["copilot-operations-*.tar.gz"],
        }
        tag = component + "/v" + versions[component]
        out = root / "release"
        out.mkdir()
        files = []
        for pattern in patterns[component]:
            (file,) = folder.glob(pattern)
            assert (
                hashlib.sha256(file.read_bytes()).hexdigest() == metadata["files_sha256"][file.name]
            )
            target = out / file.name
            target.write_bytes(file.read_bytes())
            files.append(target)
        manifest = {
            "component": component,
            "version": versions[component],
            "source_commit": run["head_sha"],
            "ci_run": run_id,
            "files_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        }
        (out / "release-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        files.append(out / "release-manifest.json")
        (out / "SHA256SUMS").write_text(
            "".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in files)
        )
        files.append(out / "SHA256SUMS")
        notes = out / "notes.md"
        notes.write_text(
            f"Independent {component} release from reviewed main commit {run['head_sha']}.\nValidated by Platform CI run {run_id}; artifacts promoted without rebuilding.\nContracts and limits are documented in this repository. No fiscal certification or production deployment is implied.\n"
        )
        existing = json.loads(gh("api", f"repos/{repo}/releases"))
        assert not any(r["tag_name"] == tag for r in existing), "Immutable release already exists"
        subprocess.run(
            [
                "gh",
                "release",
                "create",
                tag,
                "--repo",
                repo,
                "--target",
                run["head_sha"],
                "--draft",
                "--latest=false",
                "--title",
                component + " " + versions[component],
                "--notes-file",
                str(notes),
                *[str(p) for p in files],
            ],
            check=True,
        )
        releases = json.loads(gh("api", f"repos/{repo}/releases"))
        (release,) = [r for r in releases if r["tag_name"] == tag]
        assert {a["name"] for a in release["assets"]} == {p.name for p in files}
        for asset in release["assets"]:
            expected = hashlib.sha256((out / asset["name"]).read_bytes()).hexdigest()
            assert asset["size"] == (out / asset["name"]).stat().st_size
            if asset.get("digest"):
                assert asset["digest"] == "sha256:" + expected
        subprocess.run(
            [
                "gh",
                "api",
                f"repos/{repo}/releases/{release['id']}",
                "--method",
                "PATCH",
                "--input",
                "-",
            ],
            input=json.dumps({"draft": False, "make_latest": "false"}).encode(),
            stdout=subprocess.DEVNULL,
            check=True,
        )
        print(tag, "published from", run["head_sha"])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--repository", required=True)
    p.add_argument("--run-id", type=int, required=True)
    p.add_argument("--component", choices=["core", "core-ui", "operations"], required=True)
    a = p.parse_args()
    publish(a.repository, a.run_id, a.component)

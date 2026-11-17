"""Candidate consumers must use all three checked artifacts and reject bad combinations."""

import hashlib
import importlib.util
import io
import json
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
with patch.object(sys, "path", [str(SCRIPTS), *sys.path]):
    spec = importlib.util.spec_from_file_location("consumer_check", SCRIPTS / "check_consumer.py")
    consumer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(consumer)


def tar(path, entries):
    with tarfile.open(path, "w:gz") as archive:
        for name, data in entries.items():
            content = data.encode()
            info = tarfile.TarInfo(name)
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))


class ConsumerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.metadata = {
            "core_version": "1.4.1",
            "core_ui_version": "0.1.1",
            "operations_version": "1.0.0",
            "source_commit": "a" * 40,
        }
        self.wheel = self.root / "copilot_core-1.4.1-py3-none-any.whl"
        with zipfile.ZipFile(self.wheel, "w") as archive:
            for name in [
                "app/sdk/__init__.py",
                "app/ontology/error_codes.ttl",
                "app/_data/skills/diagnose_incident.yaml",
                "app/admin/templates/index.html",
                "copilot_core-1.4.1.dist-info/licenses/LICENSE",
            ]:
                archive.writestr(name, "fixture")
        tar(self.root / "copilot_core-1.4.1.tar.gz", {"core/README.md": "fixture"})
        self.ui = self.root / "copilot-core-ui-0.1.1.tgz"
        tar(
            self.ui,
            {
                "package/package.json": json.dumps(
                    {"name": "@copilot/core-ui", "version": "0.1.1"}
                ),
                **{
                    f"package/{name}": "fixture"
                    for name in [
                        "dist/index.js",
                        "dist/index.d.ts",
                        "dist/styles.css",
                        "LICENSE",
                        "README.md",
                    ]
                },
            },
        )
        self.operations = self.root / "copilot-operations-1.0.0.tar.gz"
        self.write_operations(["1.4.1"])

    def write_operations(self, versions):
        tar(
            self.operations,
            {
                "MANIFEST.json": json.dumps(
                    {
                        "operations_version": "1.0.0",
                        "compatible_core_versions": versions,
                        "source_commit": self.metadata["source_commit"],
                        "files_sha256": {},
                    }
                ),
                "README.md": "fixture",
            },
        )
        (self.root / "distribution.json").write_text(json.dumps(self.metadata))
        (self.root / "SHA256SUMS").write_text(
            "".join(
                f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n"
                for p in self.root.iterdir()
                if p.name != "SHA256SUMS"
            )
        )

    def test_candidate_manifest_replaces_all_components_and_hashes(self):
        (self.root / "shared-libraries.json").write_text(
            json.dumps({"source_repository": "fixture"})
        )
        candidate = consumer.candidate_manifest(
            self.root, self.metadata, self.wheel, self.ui, self.operations
        )
        for key, artifact in [
            ("core", self.wheel),
            ("core_ui", self.ui),
            ("operations", self.operations),
        ]:
            self.assertEqual(candidate[key]["url"], artifact.as_uri())
            self.assertEqual(
                candidate[key]["sha256"], hashlib.sha256(artifact.read_bytes()).hexdigest()
            )
        self.assertEqual(candidate["source_commit"], self.metadata["source_commit"])
        self.assertEqual(candidate["source_repository"], "fixture")

    def test_incompatible_operations_rejected_before_clone(self):
        self.write_operations(["9.9.9"])
        with patch.object(consumer, "run") as run:
            with self.assertRaisesRegex(ValueError, "Operations/core provenance mismatch"):
                consumer.check(self.root, "fixture", "b" * 40, "fisc")
            run.assert_not_called()

    def test_tampered_operations_rejected_before_clone(self):
        self.operations.write_bytes(b"tampered")
        with patch.object(consumer, "run") as run:
            with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
                consumer.check(self.root, "fixture", "b" * 40, "iic")
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()

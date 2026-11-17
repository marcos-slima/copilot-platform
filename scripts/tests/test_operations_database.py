"""Disposable operations checks must clean up on validation failure."""

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

SCRIPT = Path(__file__).resolve().parents[1] / "verify_shared_distribution.py"
spec = importlib.util.spec_from_file_location("shared_verify", SCRIPT)
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.driver = MagicMock()
        self.engine = MagicMock()
        self.url = self.engine.make_url.return_value
        self.url.get_backend_name.return_value = "postgresql"
        self.url.set.return_value = self.url
        self.url.render_as_string.return_value = "fixture-database-url"
        self.connection = self.driver.connect.return_value
        self.cursor = self.connection.cursor.return_value.__enter__.return_value
        self.modules = patch.dict(
            sys.modules, {"psycopg2": self.driver, "sqlalchemy.engine": self.engine}
        )
        self.modules.start()
        self.addCleanup(self.modules.stop)

    def test_validation_failure_drops_only_created_database(self):
        with (
            self.assertRaisesRegex(RuntimeError, "validation failed"),
            verify.disposable_database("fixture-admin-url"),
        ):
            raise RuntimeError("validation failed")
        statements = [call.args[0] for call in self.driver.sql.SQL.call_args_list]
        self.assertEqual(
            statements, ["CREATE DATABASE {} TEMPLATE template0", "DROP DATABASE {} WITH (FORCE)"]
        )
        identifiers = [call.args[0] for call in self.driver.sql.Identifier.call_args_list]
        self.assertEqual(identifiers[0], identifiers[1])
        self.assertTrue(identifiers[0].startswith("copilot_artifact_"))
        self.assertEqual(self.cursor.execute.call_count, 2)
        self.connection.close.assert_called_once()

    def test_create_failure_closes_connection_without_drop(self):
        self.cursor.execute.side_effect = RuntimeError("create refused")
        with (
            self.assertRaisesRegex(RuntimeError, "create refused"),
            verify.disposable_database("fixture-admin-url"),
        ):
            self.fail("must not run validation")
        self.assertEqual(self.cursor.execute.call_count, 1)
        self.connection.close.assert_called_once()

    def test_non_postgres_rejected_before_connect(self):
        self.url.get_backend_name.return_value = "sqlite"
        with (
            self.assertRaisesRegex(ValueError, "PostgreSQL"),
            verify.disposable_database("fixture-admin-url"),
        ):
            self.fail("must not run validation")
        self.driver.connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()

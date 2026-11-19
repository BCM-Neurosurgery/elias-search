"""Check fresh setup and preservation of existing deployment state."""
import os
from pathlib import Path
import shutil
import sqlite3
import stat
import subprocess
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[1] / "prepare_runtime_files.sh"


class RuntimeFilesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="elias runtime files ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.backend = self.root / "elias-search-server"
        self.backend.mkdir()
        scripts = self.root / "scripts"
        scripts.mkdir()
        self.helper = scripts / HELPER.name
        shutil.copyfile(HELPER, self.helper)

    def prepare(self, *names):
        # Deliberately run outside the checkout to verify paths are anchored there.
        return subprocess.run(
            ["bash", str(self.helper), *names],
            cwd=self.root.parent,
            capture_output=True,
            text=True,
        )

    def test_fresh_setup_creates_empty_private_files(self):
        result = self.prepare("db.sqlite3", "dj_log.log")
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ("db.sqlite3", "dj_log.log"):
            path = self.backend / name
            self.assertTrue(path.is_file())
            self.assertEqual(path.read_bytes(), b"")
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_repeated_setup_preserves_database_log_and_timestamps(self):
        database = self.backend / "db.sqlite3"
        with sqlite3.connect(database) as con:
            con.execute("CREATE TABLE deployment_state (value TEXT)")
            con.execute("INSERT INTO deployment_state VALUES ('keep this state')")
        log = self.backend / "dj_log.log"
        log.write_text("existing log\n")
        original = {}
        for path in (database, log):
            os.utime(path, ns=(1_500_000_000_000_000_000,) * 2)
            original[path] = (path.read_bytes(), path.stat().st_mtime_ns)
        for _ in range(2):
            result = self.prepare("db.sqlite3", "dj_log.log")
            self.assertEqual(result.returncode, 0, result.stderr)
        for path, (contents, modified) in original.items():
            self.assertEqual(path.read_bytes(), contents)
            self.assertEqual(path.stat().st_mtime_ns, modified)

    def test_existing_directories_stop_before_any_file_is_created(self):
        for name in ("db.sqlite3", "dj_log.log"):
            with self.subTest(name=name):
                wrong_path = self.backend / name
                wrong_path.mkdir()
                result = self.prepare("db.sqlite3", "dj_log.log")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Expected a regular runtime file", result.stderr)
                self.assertEqual(list(self.backend.iterdir()), [wrong_path])
                wrong_path.rmdir()

    def test_symlinks_are_rejected_without_changing_targets(self):
        target = self.root / "existing-state"
        target.write_text("preserve this\n")
        link = self.backend / "db.sqlite3"
        for link_target in (target, self.root / "missing-state"):
            with self.subTest(target=link_target):
                link.symlink_to(link_target)
                result = self.prepare("db.sqlite3", "dj_log.log")
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(link.is_symlink())
                self.assertFalse((self.backend / "dj_log.log").exists())
                self.assertEqual(target.read_text(), "preserve this\n")
                self.assertFalse((self.root / "missing-state").exists())
                link.unlink()

    def test_development_prepares_only_log_file(self):
        result = self.prepare("dj_log.log")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.backend / "dj_log.log").is_file())
        self.assertFalse((self.backend / "db.sqlite3").exists())

    def test_invalid_arguments_stop_before_creating_files(self):
        for names in ((), ("db.sqlite3", "../unexpected")):
            with self.subTest(names=names):
                result = self.prepare(*names)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(list(self.backend.iterdir()), [])


if __name__ == "__main__":
    unittest.main()

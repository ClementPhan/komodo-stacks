import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.stack_helpers import inject_dummy_secrets

ROOT = Path(__file__).resolve().parents[1]


class YamlLintTests(unittest.TestCase):
    def test_yaml_files_pass_yamllint(self):
        yamllint = shutil.which("yamllint")
        self.assertIsNotNone(yamllint, "Install yamllint to run this test")
        assert yamllint is not None

        with tempfile.TemporaryDirectory() as temporary_directory:
            test_root = Path(temporary_directory)
            shutil.copytree(ROOT / "stacks", test_root / "stacks")
            shutil.copytree(
                ROOT / ".github" / "workflows",
                test_root / ".github" / "workflows",
            )
            shutil.copy2(ROOT / ".yamllint", test_root / ".yamllint")

            inject_dummy_secrets(test_root)

            lint = subprocess.run(
                [
                    yamllint,
                    "-c",
                    ".yamllint",
                    ".github/workflows",
                    "stacks",
                ],
                cwd=test_root,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, lint.returncode, lint.stdout + lint.stderr)


if __name__ == "__main__":
    unittest.main()

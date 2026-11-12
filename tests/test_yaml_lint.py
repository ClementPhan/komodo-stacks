import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inject_dummy_secrets(test_root):
    replacements = (
        (r"(?:\{\{)?op://docker/home_address/url/url(?:\}\})?", "example.com"),
        (r"(?:\{\{)?op://docker/TrueNas/config/services_ip(?:\}\})?", "10.0.0.0"),
        (r"(?:\{\{)?op://docker/[a-zA-Z0-9/\-]*(?:\}\})?", "DUMMY_SECRET"),
    )
    for path in test_root.rglob("*"):
        if path.is_file() and path.suffix in {".yaml", ".yml", ".env"}:
            with path.open(newline="") as source:
                contents = source.read().replace("\r\n", "\n")
            for pattern, replacement in replacements:
                contents = re.sub(pattern, replacement, contents)
            with path.open("w", newline="") as destination:
                destination.write(contents)


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

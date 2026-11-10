import re
import tomllib
import unittest

from tests.stack_helpers import ROOT, STACKS

SYNCS = ROOT / "syncs"
EXPECTED_REPO = "ClementPhan/komodo-stacks"
ENV_ASSIGNMENT = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=")
ENV_REFERENCE = re.compile(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)")
BUILTIN_ENVIRONMENT_VARIABLES = {"PWD"}


def get_sync_entries(sync_file):
    sync = tomllib.loads(sync_file.read_text(encoding="utf-8"))
    sync_entries = sync.get("stack", [])
    return sync_entries if isinstance(sync_entries, list) else [sync_entries]


def get_declared_environment_variables(stack_dir, sync_entries):
    variables = set(BUILTIN_ENVIRONMENT_VARIABLES)
    env_files = set(stack_dir.glob("*.env"))
    env_files.add(stack_dir / ".env")

    for env_file in env_files:
        if not env_file.is_file():
            continue
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.lstrip().startswith("#"):
                continue
            match = ENV_ASSIGNMENT.match(line)
            if match:
                variables.add(match.group(1))

    for entry in sync_entries:
        environment = entry.get("config", {}).get("environment", "")
        for line in environment.splitlines():
            match = ENV_ASSIGNMENT.match(line)
            if match:
                variables.add(match.group(1))

    return variables


class StackSyncTests(unittest.TestCase):
    def test_every_stack_has_a_sync(self):
        missing_syncs = [
            compose_file.parent.name
            for compose_file in STACKS.glob("**/compose.yaml")
            if not (SYNCS / f"{compose_file.parent.name}.toml").is_file()
        ]
        self.assertEqual(
            [],
            sorted(missing_syncs),
            "Stacks missing sync files: " + ", ".join(sorted(missing_syncs)),
        )

    def test_sync_branch_is_main_or_undefined(self):
        invalid_branches = {}
        for compose_file in STACKS.glob("**/compose.yaml"):
            stack_name = compose_file.parent.name
            sync_file = SYNCS / f"{stack_name}.toml"
            if not sync_file.is_file():
                continue

            branches = [
                entry.get("config", {}).get("branch")
                for entry in get_sync_entries(sync_file)
            ]
            invalid = [branch for branch in branches if branch not in (None, "main")]
            if invalid:
                invalid_branches[stack_name] = invalid

        self.assertEqual(
            {},
            invalid_branches,
            "Stack sync branches must be omitted or set to 'main'",
        )

    def test_sync_repo_matches_repository(self):
        invalid_repos = {}
        for compose_file in STACKS.glob("**/compose.yaml"):
            stack_name = compose_file.parent.name
            sync_file = SYNCS / f"{stack_name}.toml"
            if not sync_file.is_file():
                continue

            for entry in get_sync_entries(sync_file):
                repo = entry.get("config", {}).get("repo")
                if repo != EXPECTED_REPO:
                    invalid_repos.setdefault(stack_name, []).append(repo)

        self.assertEqual(
            {},
            invalid_repos,
            f"Stack sync repos must be '{EXPECTED_REPO}'",
        )

    def test_sync_run_directory_matches_stack(self):
        invalid_run_directories = {}
        for compose_file in STACKS.glob("**/compose.yaml"):
            stack_name = compose_file.parent.name
            sync_file = SYNCS / f"{stack_name}.toml"
            if not sync_file.is_file():
                continue

            for entry in get_sync_entries(sync_file):
                run_directory = entry.get("config", {}).get("run_directory")
                expected_directory = f"stacks/{stack_name}"
                if run_directory != expected_directory:
                    invalid_run_directories.setdefault(stack_name, []).append(
                        run_directory
                    )

        self.assertEqual(
            {},
            invalid_run_directories,
            "Stack sync run_directories must exactly match stacks/<stack> without './'",
        )

    def test_compose_environment_variables_are_defined_in_stack_or_sync(self):
        undefined_variables = {}
        for compose_file in STACKS.glob("**/compose.yaml"):
            stack_name = compose_file.parent.name
            sync_file = SYNCS / f"{stack_name}.toml"
            sync_entries = get_sync_entries(sync_file) if sync_file.is_file() else []
            declared_variables = get_declared_environment_variables(
                compose_file.parent, sync_entries
            )
            referenced_variables = set()
            for line in compose_file.read_text(encoding="utf-8").splitlines():
                if line.lstrip().startswith("#"):
                    continue
                referenced_variables.update(ENV_REFERENCE.findall(line))

            undefined = sorted(referenced_variables - declared_variables)
            if undefined:
                undefined_variables[stack_name] = undefined

        self.assertEqual(
            {},
            undefined_variables,
            "Compose variables must be defined in stack env files or sync environment",
        )


if __name__ == "__main__":
    unittest.main()
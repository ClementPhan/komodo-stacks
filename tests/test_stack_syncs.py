import tomllib
import unittest

from tests.stack_helpers import ROOT, STACKS

SYNCS = ROOT / "syncs"


def get_stack_entries(sync_file):
    sync = tomllib.loads(sync_file.read_text(encoding="utf-8"))
    stack_entries = sync.get("stack", [])
    return stack_entries if isinstance(stack_entries, list) else [stack_entries]


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
                for entry in get_stack_entries(sync_file)
            ]
            invalid = [branch for branch in branches if branch not in (None, "main")]
            if invalid:
                invalid_branches[stack_name] = invalid

        self.assertEqual(
            {},
            invalid_branches,
            "Stack sync branches must be omitted or set to 'main'",
        )


if __name__ == "__main__":
    unittest.main()
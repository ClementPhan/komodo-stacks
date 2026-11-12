import re
from pathlib import Path

# Global constants for tests
ROOT = Path(__file__).resolve().parents[1]
STACKS = ROOT / "stacks"
GATUS_CONFIG = STACKS / "gatus" / "config" / "config.yaml"
NON_HTTP_STACKS = {"1password"}


# Regular expressions for traefik routers
ROUTER_RULE = re.compile(r"^\s*traefik\.http\.routers\.([^.]+)\.rule:\s*(.+)$")
HOST_MATCHER = re.compile(r"Host\s*\(([^)]*)\)")


def get_traefik_routers(compose_file):
    routers = []
    for line in compose_file.read_text(encoding="utf-8").splitlines():
        match = ROUTER_RULE.match(line)
        if not match:
            continue

        router_name, rule = match.groups()
        hosts = {
            host.lower()
            for host_rule in HOST_MATCHER.findall(rule)
            for host in re.findall(r"`([^`]+)`", host_rule)
        }
        routers.append((router_name.lower(), hosts))

    return routers


def inject_dummy_secrets(test_root):
    replacements = (
        (r"(?:\{\{)?op://docker/home_address/url/url(?:\}\})?", "example.com"),
        (r"(?:\{\{)?op://docker/TrueNas/config/services_ip(?:\}\})?", "10.0.0.0"),
        (r"(?:\{\{)?op://docker/[a-zA-Z0-9/\-]*(?:\}\})?", "DUMMY_SECRET"),
    )
    for path in test_root.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        if path.suffix not in {".yaml", ".yml", ".env"}:
            continue

        with path.open(encoding="utf-8", newline="") as source:
            contents = source.read().replace("\r\n", "\n")
        for pattern, replacement in replacements:
            contents = re.sub(pattern, replacement, contents)
        with path.open("w", encoding="utf-8", newline="") as destination:
            destination.write(contents)


if __name__ == "__main__":
    inject_dummy_secrets(ROOT)

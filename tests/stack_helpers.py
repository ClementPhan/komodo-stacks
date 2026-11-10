import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STACKS = ROOT / "stacks"
GATUS_CONFIG = STACKS / "gatus" / "config" / "config.yaml"
NON_HTTP_STACKS = {"1password"}

ROUTER_RULE = re.compile(
    r"^\s*traefik\.http\.routers\.([^.]+)\.rule:\s*(.+)$"
)
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
import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
STACKS = ROOT / "stacks"
GATUS_CONFIG = STACKS / "gatus" / "config" / "config.yaml"
ROUTER_RULE = re.compile(r"^\s*traefik\.http\.routers\..+\.rule:\s*(.+)$")
HOST_MATCHER = re.compile(r"Host\s*\(([^)]*)\)")
URL_MATCHER = re.compile(r"^\s+url:\s*[\"']?([^\"'\s]+)", re.MULTILINE)


class UptimeMonitoringTests(unittest.TestCase):
    def test_all_traefik_router_hosts_are_monitored(self):
        router_hosts = set()
        for compose_file in STACKS.glob("**/compose.yaml"):
            for line in compose_file.read_text(encoding="utf-8").splitlines():
                rule = ROUTER_RULE.match(line)
                if rule:
                    for host_rule in HOST_MATCHER.findall(rule.group(1)):
                        router_hosts.update(re.findall(r"`([^`]+)`", host_rule))

        self.assertTrue(router_hosts, "No Traefik Host() router rules were found")

        config = GATUS_CONFIG.read_text(encoding="utf-8")
        monitored_hosts = {
            urlsplit(url).hostname.lower()
            for url in URL_MATCHER.findall(config)
            if urlsplit(url).hostname
        }
        missing_hosts = sorted(
            host for host in router_hosts if host.lower() not in monitored_hosts
        )

        self.assertEqual(
            [],
            missing_hosts,
            "Traefik router hosts missing from Gatus endpoints: "
            + ", ".join(missing_hosts),
        )


if __name__ == "__main__":
    unittest.main()

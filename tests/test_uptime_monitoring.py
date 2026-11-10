import re
import unittest
from urllib.parse import urlsplit

from tests.stack_helpers import GATUS_CONFIG, STACKS, get_traefik_routers

URL_MATCHER = re.compile(r"^\s+url:\s*[\"']?([^\"'\s]+)", re.MULTILINE)


class UptimeMonitoringTests(unittest.TestCase):
    def test_all_traefik_router_hosts_are_monitored(self):
        router_hosts = set()
        for compose_file in STACKS.glob("**/compose.yaml"):
            for _, hosts in get_traefik_routers(compose_file):
                router_hosts.update(hosts)

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

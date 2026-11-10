import unittest

from tests.stack_helpers import NON_HTTP_STACKS, STACKS, get_traefik_routers


class TraefikTests(unittest.TestCase):
    def test_all_http_stacks_have_unique_router_hosts_and_names(self):
        host_stacks = {}
        router_name_stacks = {}
        stacks_without_hosts = []

        for compose_file in STACKS.glob("**/compose.yaml"):
            stack_name = compose_file.parent.name
            if stack_name in NON_HTTP_STACKS:
                continue

            routers = get_traefik_routers(compose_file)
            hosts = {host for _, router_hosts in routers for host in router_hosts}
            if not hosts:
                stacks_without_hosts.append(stack_name)

            for host in hosts:
                host_stacks.setdefault(host, []).append(stack_name)
            for router_name in {name for name, _ in routers}:
                router_name_stacks.setdefault(router_name, []).append(stack_name)

        duplicate_hosts = {
            host: sorted(stacks)
            for host, stacks in host_stacks.items()
            if len(stacks) > 1
        }
        duplicate_router_names = {
            name: sorted(stacks)
            for name, stacks in router_name_stacks.items()
            if len(stacks) > 1
        }

        self.assertEqual(
            [],
            sorted(stacks_without_hosts),
            "Compose stacks missing a Traefik Host() router: "
            + ", ".join(sorted(stacks_without_hosts)),
        )
        self.assertEqual(
            {},
            duplicate_hosts,
            "Traefik router hostnames must be unique across Compose stacks",
        )
        self.assertEqual(
            {},
            duplicate_router_names,
            "Traefik router names must be unique across Compose stacks",
        )


if __name__ == "__main__":
    unittest.main()
#!/usr/bin/env python
from __future__ import print_function

import argparse

import common

GENERAL_TEMPLATE = """
# General.
set system host-name router-{id}
"""

PORTS_TEMPLATE = """
# Ports.
set interfaces ethernet eth0 vif 10
set interfaces ethernet eth0 vif 20
set interfaces bridge br10
set interfaces ethernet eth0 vif 10 bridge-group bridge br10
set interfaces ethernet eth1 bridge-group bridge br10
set interfaces ethernet eth2 bridge-group bridge br10
set interfaces ethernet eth5 bridge-group bridge br10
set interfaces ethernet eth1 poe output 24v
set interfaces ethernet eth2 poe output 24v
"""

ADDRESSING_TEMPLATE = """
# Addressing.
set interfaces bridge br10 address 10.10.{id}.1/16
set interfaces ethernet eth0 vif 20 address 10.20.0.{id}/24
"""

ADDRESSING_LINK_A_TEMPLATE = """
set interfaces ethernet eth3 address 10.20.{link_a}.{id}/24
"""

ADDRESSING_LINK_B_TEMPLATE = """
set interfaces ethernet eth4 address 10.20.{link_b}.{id}/24
"""

ROUTING_TEMPLATE = """
# Routing.
set protocols ospf parameters router-id 10.10.{id}.1
set protocols ospf area 0.0.0.0 area-type normal
set protocols ospf area 0.0.0.0 network 10.20.0.0/16
set policy prefix-list redistribute rule 10
set policy prefix-list redistribute rule 10 action permit
set policy prefix-list redistribute rule 10 prefix 10.20.0.0/16
set policy route-map redistribute rule 10
set policy route-map redistribute rule 10 action permit
set policy route-map redistribute rule 10 match ip address prefix-list redistribute
set protocols ospf redistribute connected
set interfaces ethernet eth3 ip ospf
set interfaces ethernet eth4 ip ospf
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--router', type=int, help="Only generate configuration for a specific router")
    args = parser.parse_args()

    routers = common.get_config('routers')
    links = common.get_config('links')

    # Generate configuration.
    for router in routers:
        if args.router and args.router != router['id']:
            continue

        print('# Router {id}'.format(**router))
        print('# -----------------------------------------------------------')
        print(GENERAL_TEMPLATE.format(**router))
        print(PORTS_TEMPLATE)

        print(ADDRESSING_TEMPLATE.format(**router))
        if router['link_a']:
            print(ADDRESSING_LINK_A_TEMPLATE.format(**router))
        if router['link_b']:
            print(ADDRESSING_LINK_B_TEMPLATE.format(**router))

        print(ROUTING_TEMPLATE.format(**router))
        print('# -----------------------------------------------------------')

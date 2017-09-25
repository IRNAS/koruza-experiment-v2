# Definitions

* `r` is the router id (**ids `0` and `254` are reserved and must not be used for any router**).
* `l` is the link id (**id `0` is reserved and must not be used for any link**).
  * `l1` is the lower link id on the pole.
  * `l2` is the higher link id on the pole.
* `Kr.l` is the KORUZA unit connected to router `r` and link `l`.

# Router ports

Each router `r` is configured with two data ports (`eth3` and `eth4`) and three management
ports (`eth0`, `eth1` and `eth2`).

Ports are connected as follows:
* `eth0` is connected to the main switch.
* `eth1` is connected to KORUZA unit (management port) with lower link id.
* `eth2` is connected to KORUZA unit (management port) with higher link id.
* `eth3` is connected to KORUZA unit (data port) with lower link id.
* `eth4` is connected to KORUZA unit (data port) with higher link id.

## VLANs

Interface `eth0` is used as a trunk to deliver tagged frames to the main switch. The following
VLAN tags are used:
* `10` is used for the management network (interface `eth0.10`).
* `20` is used for the data network (interface `eth0.20`).

## Bridges

The following bridges are configured:
* `br10` with ports `eth0.10`, `eth1` and `eth2`.

# Router addressing

There are two distinct subnets:
* `10.10.0.0/16` is used for the management network.
* `10.20.0.0/16` is used for the data network.

Ports are assigned addresses as follows:
* `br10` is assigned `10.10.r.1/16`.
* `eth0.20` is assigned `10.20.0.r/24`.
* KORUZA unit connected to `eth1` is assigned `10.10.r.2/16`.
* KORUZA unit connected to `eth2` is assigned `10.10.r.3/16`.
* `eth3` is assigned `10.20.l1.r/24`.
* `eth4` is assigned `10.20.l2.r/24`.

# Main switch addressing

The main switch uses the reserved subnet `10.10.0.0/24` for its addresses. It is assigned
the address `10.10.0.1/16` on `switch0.10`.

# Routing

OSPF is configured on all routers in order to route data traffic between them. Each router is
assigned a router ID in the format `10.10.r.1`.

A single OSPF area `0.0.0.0` is used, configured to route `10.20.0.0/16`. Routes towards all
connected interfaces are redistributed.

Only interfaces `eth3` and `eth4` (data ports) participate in routing.

# Example configuration

The following example configures EdgeRouter with ids 1 and 2, connected to links 1, 2 and 3.
**It assumes that a full factory reset has been performed and all configuration has been
cleared.**

## Router 1

```
# Ports.
set interfaces ethernet eth0 vif 10
set interfaces ethernet eth0 vif 20
set interfaces bridge br10
set interfaces ethernet eth0 vif 10 bridge-group bridge br10
set interfaces ethernet eth1 bridge-group bridge br10
set interfaces ethernet eth2 bridge-group bridge br10
set interfaces ethernet eth1 poe output 24v
set interfaces ethernet eth2 poe output 24v

# Addressing.
set interfaces bridge br10 address 10.10.1.1/16
set interfaces ethernet eth0 vif 20 address 10.20.0.1/24
set interfaces ethernet eth3 address 10.20.1.1/24
set interfaces ethernet eth4 address 10.20.2.1/24

# Routing.
set protocols ospf parameters router-id 10.10.1.1
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
```

## Router 2
```
# Ports.
set interfaces ethernet eth0 vif 10
set interfaces ethernet eth0 vif 20
set interfaces bridge br10
set interfaces ethernet eth0 vif 10 bridge-group bridge br10
set interfaces ethernet eth1 bridge-group bridge br10
set interfaces ethernet eth2 bridge-group bridge br10
set interfaces ethernet eth1 poe output 24v
set interfaces ethernet eth2 poe output 24v

# Addressing.
set interfaces bridge br10 address 10.10.2.1/16
set interfaces ethernet eth0 vif 20 address 10.20.0.2/24
set interfaces ethernet eth3 address 10.20.1.2/24
set interfaces ethernet eth4 address 10.20.3.2/24

# Routing.
set protocols ospf parameters router-id 10.10.2.1
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
```

# Generating configuration

To generate the configuration for multiple routers, edit `config.yml` based on
your topology and then run:
```
python scripts/generate-config.py
```

This will output configuration for all the routers/links specified in your topology
file.


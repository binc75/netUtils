# How to create VLAN on OpenVSwitch

## Create 2 new tap interfaces
``` bash
root@figino:~# ip tuntap add mode tap vport3
root@figino:~# ip tuntap add mode tap vport4
```

## Add the 2 new interfaces to the switch on VLAN 234 
***this is a non tagget port, no need to configure vlan on client)***
``` bash
root@figino:~# ovs-vsctl add-port NB_bridge vport3 tag=234
root@figino:~# ovs-vsctl add-port NB_bridge vport4 tag=234
```

## Verify
```bash
root@figino:~# ovs-vsctl show
f8af26f9-fc1d-48ee-a866-f31b06529f66
    Bridge NB_bridge
        Port "wlp7s0"
            Interface "wlp7s0"
        Port NB_bridge
            Interface NB_bridge
                type: internal
        Port "veth2"
            Interface "veth2"
        Port "vport1"
            Interface "vport1"
        Port "vport2"
            Interface "vport2"
        Port "veth0"
            Interface "veth0"
        Port "vport3"
            tag: 234
            Interface "vport3"
        Port "vport4"
            tag: 234
            Interface "vport4"
    ovs_version: "2.5.5"
```


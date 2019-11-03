# 2 x OpenVSwitch + NS router
Setup the 2 virtual switches, the **tap** interfaces and the virtual interfaces
``` bash
ovs-vsctl add-br switch1
ovs-vsctl add-br switch2
ovs-vsctl show
ip addr

ip link set up dev switch1
ip link set up dev switch2
ip link set up dev vport1
ip link set up dev vport2

ip tuntap add mode tap vport1
ip tuntap add mode tap vport2
ip tuntap add mode tap vport3
ip tuntap add mode tap vport4

ip link set up dev vport1
ip link set up dev vport2
ip link set up dev vport3
ip link set up dev vport4

ovs-vsctl add-port switch1 vport1
ovs-vsctl add-port switch1 vport2
ovs-vsctl add-port switch2 vport3
ovs-vsctl add-port switch2 vport4
ovs-vsctl show

ip netns add router_ns
ip netns list

ip link add veth0-router type veth peer name veth0-switch
ip link add veth1-router type veth peer name veth1-switch

ip link set up veth0-router
ip link set up veth0-switch
ip link set up veth1-router
ip link set up veth1-switch

ip link set veth0-router netns router_ns
ip link set veth1-router netns router_ns

ovs-vsctl add-port switch1 veth0-switch
ovs-vsctl add-port switch2 veth1-switch
ovs-vsctl show
```

**At this point bring up 4 VMs and connect the vportX devices**  
**virt1 and virt2 are on the same switch, virt3 and virt4 on the other**  

## ROUTER SETUP
```bash
root@figino:~# ip netns exec router_ns ip addr show
 1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN group default qlen 1
     link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
 14: veth0-router@if13: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
     link/ether 52:3f:67:50:04:c7 brd ff:ff:ff:ff:ff:ff link-netnsid 0
 16: veth1-router@if15: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
     link/ether 42:53:dd:02:84:b3 brd ff:ff:ff:ff:ff:ff link-netnsid 0
root@figino:~#

root@figino:~# ip netns exec router_ns ip addr add 192.168.1.1/24 dev veth0-router
root@figino:~# ip netns exec router_ns ip addr add 192.168.2.1/24 dev veth1-router
root@figino:~# ip netns exec router_ns ip link set up dev veth0-router
root@figino:~# ip netns exec router_ns ip link set up dev veth1-router

root@figino:~# ip netns exec router_ns ip addr show
1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN group default qlen 1
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
14: veth0-router@if13: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 52:3f:67:50:04:c7 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet 192.168.1.1/24 scope global veth0-router
       valid_lft forever preferred_lft forever
    inet6 fe80::503f:67ff:fe50:4c7/64 scope link 
       valid_lft forever preferred_lft forever
16: veth1-router@if15: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 42:53:dd:02:84:b3 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet 192.168.2.1/24 scope global veth1-router
       valid_lft forever preferred_lft forever
    inet6 fe80::4053:ddff:fe02:84b3/64 scope link 
       valid_lft forever preferred_lft forever
root@figino:~# 
```

... at this point the VMs should be able to ping across the router!


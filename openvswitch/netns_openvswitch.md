# Quick example on how to use OpenVSitch and network namespaces

## Schema
Here the schema of the setup we are going to implement
```
       |-------------|  - this switch is in the default netns
       | openvswitch |  - 2 ports here called : net1-ovs & net2-ovs
       |-------------|
    net1-ovs     net2-ovs
         +           +
         +           +
         +           +
  net1-netns       net2-netns
  |-----------|   |-----------| 
  | namespace |   | namespace |
  |   net1    |   |   net2    |
  |-----------|   |-----------|

```

## Net NS setup

### Create 2 new network domains
``` bash
ip netns add net1
ip netns add net2
```

### List network domains
``` bash
root@figino:~# ip netns list
net2
net1
root@figino:~#
root@figino:~# ls -l /var/run/netns/
total 0
-r--r--r-- 1 root root 0 May 10 07:58 net1
-r--r--r-- 1 root root 0 May 10 07:58 net2
root@figino:~# 
```

### execute commmands from inside a network domain
``` bash
root@figino:~# ip netns exec net1 ip a
   1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN group default 
       link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00

root@figino:~# ip netns exec net2 ip a
   1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN group default 
       link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
```

## OpenVSwitch setup
### Install openvswitch 
``` bash
root@figino:~# apt-get install openvswitch-switch openvswitch-common
root@figino:~# /etc/init.d/openvswitch-switch status
openvswitch-switch start/running
root@figino:~# 
```

### Create a new virtual switch
``` bash
root@figino:~# ovs-vsctl add-br my_virtual_switch
root@figino:~# ovs-vsctl show
 f8af26f9-fc1d-48ee-a866-f31b06529f66
    Bridge my_virtual_switch
        Port my_virtual_switch
            Interface my_virtual_switch
                type: internal
    ovs_version: "2.0.2"
```

## Connect the NS to the virtual switch
To connect the namespaces to our switch, we’ll use ‘veth’ pairs.  
veth (Virtual Ethernet) is a type of network device which always comes in pairs.  
You can imagine this pair as a tube. Everything you’ll send through one end of the  tube, will come out  at the other end.

### Create veth device to connect "net1" namespace to the virtual switch.
``` bash
root@figino:~# ip link add net1-netns type veth peer name net1-ovs
root@figino:~# ip a
   ...
   4: ovs-system: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default 
       link/ether 42:04:28:05:8b:cd brd ff:ff:ff:ff:ff:ff
   5: net1-ovs: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
       link/ether 92:3e:13:8a:58:bf brd ff:ff:ff:ff:ff:ff
       inet6 fe80::903e:13ff:fe8a:58bf/64 scope link 
          valid_lft forever preferred_lft forever
   6: net1-netns: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
       link/ether f2:b3:53:da:e4:7c brd ff:ff:ff:ff:ff:ff
       inet6 fe80::f0b3:53ff:feda:e47c/64 scope link 
          valid_lft forever preferred_lft forever
```


### Attach "net1-netns" in "net1" namespace
``` bash
root@figino:~# ip link set net1-netns netns net1
```

You should not see ‘net1-netns’ anymore in the ‘default’ namespace, since we put it in ‘net1’ namespace

``` bash
root@figino:~# ip a
   1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default 
       link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
       inet 127.0.0.1/8 scope host lo
          valid_lft forever preferred_lft forever
       inet6 ::1/128 scope host 
          valid_lft forever preferred_lft forever
   2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
       link/ether e0:3f:49:44:ab:7f brd ff:ff:ff:ff:ff:ff
       inet 148.187.160.38/24 brd 148.187.160.255 scope global eth0
          valid_lft forever preferred_lft forever
       inet6 2001:620:808:2000:506c:3c54:6370:a918/64 scope global temporary dynamic 
          valid_lft 595722sec preferred_lft 3416sec
       inet6 2001:620:808:2000:45e3:4bfd:aff6:af50/64 scope global temporary deprecated dynamic 
          valid_lft 509934sec preferred_lft 0sec
       inet6 2001:620:808:2000:404e:8768:3e3e:99e0/64 scope global temporary deprecated dynamic 
          valid_lft 424146sec preferred_lft 0sec
       inet6 2001:620:808:2000:e23f:49ff:fe44:ab7f/64 scope global dynamic 
          valid_lft 2591816sec preferred_lft 3416sec
       inet6 fe80::e23f:49ff:fe44:ab7f/64 scope link 
          valid_lft forever preferred_lft forever
   3: docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
       link/ether 02:42:a6:b7:62:f1 brd ff:ff:ff:ff:ff:ff
       inet 172.17.0.1/16 scope global docker0
          valid_lft forever preferred_lft forever
   4: ovs-system: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default 
       link/ether 42:04:28:05:8b:cd brd ff:ff:ff:ff:ff:ff
   5: net1-ovs: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc pfifo_fast state DOWN group default qlen 1000
       link/ether 92:3e:13:8a:58:bf brd ff:ff:ff:ff:ff:ff
       inet6 fe80::903e:13ff:fe8a:58bf/64 scope link 
          valid_lft forever preferred_lft forever
   
root@figino:~# ip netns exec net1 ip a
   1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN group default 
       link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
   6: net1-netns: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
       link/ether f2:b3:53:da:e4:7c brd ff:ff:ff:ff:ff:ff
```

### Add the other end (net1-ovs) to the virtual switch
``` bash
root@figino:~# ovs-vsctl add-port my_virtual_switch net1-ovs
root@figino:~# ovs-vsctl show
 f8af26f9-fc1d-48ee-a866-f31b06529f66
    Bridge my_virtual_switch
        Port my_virtual_switch
            Interface my_virtual_switch
                type: internal
        Port "net1-ovs"
            Interface "net1-ovs"
    ovs_version: "2.0.2"
root@figino:~# 
```

Repeat the same for "net2
``` bash
root@figino:~# ip link add net2-netns type veth peer name net2-ovs
root@figino:~# ip link set net2-netns netns net2
root@figino:~# ovs-vsctl add-port my_virtual_switch net2-ovs
```

### Bring up our devices in the ‘default’ namespace
``` bash
root@figino:~# ip link set net1-ovs up
root@figino:~# ip link set net2-ovs up
```

### Bring up bring up all the devices in ‘net1’ and ‘net2’ namespaces
``` bash
root@figino:~# ip netns exec net1 ip link set dev lo up
root@figino:~# ip netns exec net1 ip link set dev net1-netns up
root@figino:~# ip netns exec net2 ip link set dev lo up
root@figino:~# ip netns exec net2 ip link set dev net2-netns up
```

### Assign addresses for both ‘net1-netns’ and ‘net2-netns’ devices in the namespces
``` bash
root@figino:~# ip netns exec net1 ip addr add 192.168.0.10/24 dev net1-netns
root@figino:~# ip netns exec net2 ip addr add 192.168.0.20/24 dev net2-netns
```

### Verify ip addr
``` bash
root@figino:~# ip netns exec net2 ip addr 
   1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default 
       link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
       inet 127.0.0.1/8 scope host lo
          valid_lft forever preferred_lft forever
       inet6 ::1/128 scope host 
          valid_lft forever preferred_lft forever
   8: net2-netns: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
       link/ether c2:d5:7d:78:b0:d5 brd ff:ff:ff:ff:ff:ff
       inet 192.168.0.20/24 scope global net2-netns
          valid_lft forever preferred_lft forever
       inet6 fe80::c0d5:7dff:fe78:b0d5/64 scope link 
          valid_lft forever preferred_lft forever

root@figino:~# ip netns exec net1 ip addr 
   1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default 
       link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
       inet 127.0.0.1/8 scope host lo
          valid_lft forever preferred_lft forever
       inet6 ::1/128 scope host 
          valid_lft forever preferred_lft forever
   6: net1-netns: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
       link/ether f2:b3:53:da:e4:7c brd ff:ff:ff:ff:ff:ff
       inet 192.168.0.10/24 scope global net1-netns
          valid_lft forever preferred_lft forever
       inet6 fe80::f0b3:53ff:feda:e47c/64 scope link 
          valid_lft forever preferred_lft forever
```

### Ping test
``` bash
root@figino:~# ip netns exec net2 ping 192.168.0.10
   PING 192.168.0.10 (192.168.0.10) 56(84) bytes of data.
   64 bytes from 192.168.0.10: icmp_seq=1 ttl=64 time=0.255 ms
   64 bytes from 192.168.0.10: icmp_seq=2 ttl=64 time=0.044 ms
   64 bytes from 192.168.0.10: icmp_seq=3 ttl=64 time=0.113 ms
   ^C
   --- 192.168.0.10 ping statistics ---
   3 packets transmitted, 3 received, 0% packet loss, time 1999ms
   rtt min/avg/max/mdev = 0.044/0.137/0.255/0.088 ms
```
``` bash
root@figino:~# ip netns exec net1 ping 192.168.0.20
   PING 192.168.0.20 (192.168.0.20) 56(84) bytes of data.
   64 bytes from 192.168.0.20: icmp_seq=1 ttl=64 time=0.169 ms
   64 bytes from 192.168.0.20: icmp_seq=2 ttl=64 time=0.047 ms
   ^C
   --- 192.168.0.20 ping statistics ---
   2 packets transmitted, 2 received, 0% packet loss, time 999ms
   rtt min/avg/max/mdev = 0.047/0.108/0.169/0.061 ms
```


## Launch a service inside a name space (net2 in this case)
``` bash
root@figino:~# ip netns exec net2 /etc/init.d/apache2 status
 * apache2 is not running

root@figino:~# ip netns exec net2 /etc/init.d/apache2 start
 * Starting web server apache2                                                                                                                        

root@figino:~# pidof apache2
13881 13749 13748 13747 13746 13745 13742

root@figino:~# ip netns identify 13881
net2
```


### Check from namespace net1 if net2 apache is reacheable
``` bash
root@figino:~# ip netns exec net1 wget http://192.168.0.20/
   --2017-05-10 09:39:10--  http://192.168.0.20/
   Connecting to 192.168.0.20:80... connected.
   HTTP request sent, awaiting response... 200 OK
   Length: unspecified [text/html]
   Saving to: ‘index.html’
   
       [ <=>                        ] 29          --.-K/s   in 0s      
   
   2017-05-10 09:39:10 (5.93 MB/s) - ‘index.html’ saved [29]
   
root@figino:~# cat index.html 
  figino.intnet.cscs.ch
  nicola
```


### Confirm that from the default namespace there is no access
``` bash
root@figino:~# wget http://192.168.0.20/
   --2017-05-10 10:01:27--  http://192.168.0.20/
   Connecting to 192.168.0.20:80... connected.
   HTTP request sent, awaiting response... Read error (Connection reset by peer) in headers.
   Retrying.
```

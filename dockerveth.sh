#!/bin/bash

# 
# Find association between docker containers and veth pair interfaces
# Run on the docker host
#

for container in $(docker ps --format '{{.ID}},{{.Names}}'); do
    contId=$(echo $container | awk -F "," '{print $1}')
    contName=$(echo $container | awk -F "," '{print $2}')
    iflink=$(docker exec -it $contId bash -c 'cat /sys/class/net/eth0/iflink')
    iflink=$(echo $iflink|tr -d '\r')
    veth=$(grep -l $iflink /sys/class/net/veth*/ifindex)
    veth=$(echo $veth|sed -e 's;^.*net/\(.*\)/ifindex$;\1;')
    echo $contId:$contName:$veth
done


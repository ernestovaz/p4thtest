#!/bin/bash 
# Stop and remove containers 
containers=($ "s4"  "s1"  "s2"  "s3"  "h1"  "h2"  "h3"  "h4" ) 
for container in "${containers[@]}"; do 
if [ $(docker ps -a -q -f name=^/${container}$) ]; then 
echo "Removing container $container..." 
docker stop $container 
docker rm $container 
    fi 
done 
 
# Removing Interfaces 
veths=(  "s1-p4-s4-p2"  "s4-p2-s1-p4"  "s1-p3-s3-p1"  "s3-p1-s1-p3"  "s2-p4-s3-p2"  "s3-p2-s2-p4"  "s2-p3-s4-p1"  "s4-p1-s2-p3"  "h4-p1-s2-p2"  "s2-p2-h4-p1"  "h3-p1-s2-p1"  "s2-p1-h3-p1"  "h2-p1-s1-p2"  "s1-p2-h2-p1"  "h1-p1-s1-p1"  "s1-p1-h1-p1" ) 
for veth in "${veths[@]}"; do 
echo "Removing interface $veth..." 
    if ip link show | grep -q $veth; then 
        sudo ip link delete $veth 
        sudo ip link del $veth 2>/dev/null 
    fi 
done 
echo "Environment Cleaned!"

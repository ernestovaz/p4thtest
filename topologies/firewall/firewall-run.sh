#!/bin/bash 
 
 
 echo "Start Switch Container s4" 
 docker run -itd --name s4 --network="none" --privileged -v shared:/codes  --workdir /codes dnredson/p4d
 alias s4="docker exec -it s4 /bin/bash" 
 alias logs4="docker exec -it s4 cat /tmp/switch.log" 
s4() { 
docker exec -it s4 /bin/bash 
} 
export -f s4
logs4() { 
docker exec -it s4 cat /tmp/switch.log 
} 
export -f logs4 
 
 echo "Start Switch Container s1" 
 docker run -itd --name s1 --network="none" --privileged -v shared:/codes  --workdir /codes dnredson/p4d
 alias s1="docker exec -it s1 /bin/bash" 
 alias logs1="docker exec -it s1 cat /tmp/switch.log" 
s1() { 
docker exec -it s1 /bin/bash 
} 
export -f s1
logs1() { 
docker exec -it s1 cat /tmp/switch.log 
} 
export -f logs1 
 
 echo "Start Switch Container s2" 
 docker run -itd --name s2 --network="none" --privileged -v shared:/codes  --workdir /codes dnredson/p4d
 alias s2="docker exec -it s2 /bin/bash" 
 alias logs2="docker exec -it s2 cat /tmp/switch.log" 
s2() { 
docker exec -it s2 /bin/bash 
} 
export -f s2
logs2() { 
docker exec -it s2 cat /tmp/switch.log 
} 
export -f logs2 
 
 echo "Start Switch Container s3" 
 docker run -itd --name s3 --network="none" --privileged -v shared:/codes  --workdir /codes dnredson/p4d
 alias s3="docker exec -it s3 /bin/bash" 
 alias logs3="docker exec -it s3 cat /tmp/switch.log" 
s3() { 
docker exec -it s3 /bin/bash 
} 
export -f s3
logs3() { 
docker exec -it s3 cat /tmp/switch.log 
} 
export -f logs3
 
 echo "Start Host Container h1" 
 docker run -itd --name h1 --network="none" --privileged -v shared:/codes --workdir /codes ernestovaz/net
 alias h1="docker exec -it h1 /bin/bash" 

 
 echo "Start Host Container h2" 
 docker run -itd --name h2 --network="none" --privileged -v shared:/codes --workdir /codes ernestovaz/net
 alias h2="docker exec -it h2 /bin/bash" 

 
 echo "Start Host Container h3" 
 docker run -itd --name h3 --network="none" --privileged -v shared:/codes --workdir /codes ernestovaz/net
 alias h3="docker exec -it h3 /bin/bash" 

 
 echo "Start Host Container h4" 
 docker run -itd --name h4 --network="none" --privileged -v shared:/codes --workdir /codes ernestovaz/net
 alias h4="docker exec -it h4 /bin/bash" 
 
 
 echo "Set PID for each container "
 PIDh1=$(docker inspect -f '{{.State.Pid}}' h1) 
PIDh2=$(docker inspect -f '{{.State.Pid}}' h2) 
PIDh3=$(docker inspect -f '{{.State.Pid}}' h3) 
PIDh4=$(docker inspect -f '{{.State.Pid}}' h4) 
PIDs4=$(docker inspect -f '{{.State.Pid}}' s4) 
PIDs1=$(docker inspect -f '{{.State.Pid}}' s1) 
PIDs2=$(docker inspect -f '{{.State.Pid}}' s2) 
PIDs3=$(docker inspect -f '{{.State.Pid}}' s3) 

 
 echo "Creating VETH Peers"
 sudo ip link add s1-p4-s4-p2 type veth peer name s4-p2-s1-p4 
sudo ip link add s1-p3-s3-p1 type veth peer name s3-p1-s1-p3 
sudo ip link add s2-p4-s3-p2 type veth peer name s3-p2-s2-p4 
sudo ip link add s2-p3-s4-p1 type veth peer name s4-p1-s2-p3 
sudo ip link add h4-p1-s2-p2 type veth peer name s2-p2-h4-p1 
sudo ip link add h3-p1-s2-p1 type veth peer name s2-p1-h3-p1 
sudo ip link add h2-p1-s1-p2 type veth peer name s1-p2-h2-p1 
sudo ip link add h1-p1-s1-p1 type veth peer name s1-p1-h1-p1 

 
 echo "Set Namespaces" 
 sudo ip link set s1-p4-s4-p2 netns $PIDs1 
sudo ip link set s4-p2-s1-p4 netns $PIDs4 
sudo ip link set s1-p3-s3-p1 netns $PIDs1 
sudo ip link set s3-p1-s1-p3 netns $PIDs3 
sudo ip link set s2-p4-s3-p2 netns $PIDs2 
sudo ip link set s3-p2-s2-p4 netns $PIDs3 
sudo ip link set s2-p3-s4-p1 netns $PIDs2 
sudo ip link set s4-p1-s2-p3 netns $PIDs4 
sudo ip link set h4-p1-s2-p2 netns $PIDh4 
sudo ip link set s2-p2-h4-p1 netns $PIDs2 
sudo ip link set h3-p1-s2-p1 netns $PIDh3 
sudo ip link set s2-p1-h3-p1 netns $PIDs2 
sudo ip link set h2-p1-s1-p2 netns $PIDh2 
sudo ip link set s1-p2-h2-p1 netns $PIDs1 
sudo ip link set h1-p1-s1-p1 netns $PIDh1 
sudo ip link set s1-p1-h1-p1 netns $PIDs1 

 
 echo "Set network interfaces" 
 sudo nsenter -t $PIDs1 -n ip addr add 10.0.4.0 dev s1-p4-s4-p2 
sudo nsenter -t $PIDs1 -n ip link set dev s1-p4-s4-p2 address 00:00:00:00:04:00 
sudo nsenter -t $PIDs1 -n ip link set s1-p4-s4-p2 up 
sudo nsenter -t $PIDs4 -n ip addr add 10.0.1.0 dev s4-p2-s1-p4 
sudo nsenter -t $PIDs4 -n ip link set dev s4-p2-s1-p4 address 00:00:00:00:01:00 
sudo nsenter -t $PIDs4 -n ip link set s4-p2-s1-p4 up 
sudo nsenter -t $PIDs1 -n ip addr add 10.0.3.0 dev s1-p3-s3-p1 
sudo nsenter -t $PIDs1 -n ip link set dev s1-p3-s3-p1 address 00:00:00:00:03:00 
sudo nsenter -t $PIDs1 -n ip link set s1-p3-s3-p1 up 
sudo nsenter -t $PIDs3 -n ip addr add 10.0.1.0 dev s3-p1-s1-p3 
sudo nsenter -t $PIDs3 -n ip link set dev s3-p1-s1-p3 address 00:00:00:00:01:00 
sudo nsenter -t $PIDs3 -n ip link set s3-p1-s1-p3 up 
sudo nsenter -t $PIDs2 -n ip addr add 10.0.3.0 dev s2-p4-s3-p2 
sudo nsenter -t $PIDs2 -n ip link set dev s2-p4-s3-p2 address 00:00:00:00:03:00 
sudo nsenter -t $PIDs2 -n ip link set s2-p4-s3-p2 up 
sudo nsenter -t $PIDs3 -n ip addr add 10.0.2.0 dev s3-p2-s2-p4 
sudo nsenter -t $PIDs3 -n ip link set dev s3-p2-s2-p4 address 00:00:00:00:02:00 
sudo nsenter -t $PIDs3 -n ip link set s3-p2-s2-p4 up 
sudo nsenter -t $PIDs2 -n ip addr add 10.0.4.0 dev s2-p3-s4-p1 
sudo nsenter -t $PIDs2 -n ip link set dev s2-p3-s4-p1 address 00:00:00:00:04:00 
sudo nsenter -t $PIDs2 -n ip link set s2-p3-s4-p1 up 
sudo nsenter -t $PIDs4 -n ip addr add 10.0.2.0 dev s4-p1-s2-p3 
sudo nsenter -t $PIDs4 -n ip link set dev s4-p1-s2-p3 address 00:00:00:00:02:00 
sudo nsenter -t $PIDs4 -n ip link set s4-p1-s2-p3 up 
sudo nsenter -t $PIDh4 -n ip addr add 10.0.2.0 dev h4-p1-s2-p2 
sudo nsenter -t $PIDh4 -n ip link set dev h4-p1-s2-p2 address 00:00:00:00:02:00 
sudo nsenter -t $PIDh4 -n ip link set h4-p1-s2-p2 up 
sudo nsenter -t $PIDs2 -n ip addr add 10.0.4.4 dev s2-p2-h4-p1 
sudo nsenter -t $PIDs2 -n ip link set dev s2-p2-h4-p1 address 00:00:00:00:04:44 
sudo nsenter -t $PIDs2 -n ip link set s2-p2-h4-p1 up 
sudo nsenter -t $PIDh3 -n ip addr add 10.0.2.0 dev h3-p1-s2-p1 
sudo nsenter -t $PIDh3 -n ip link set dev h3-p1-s2-p1 address 00:00:00:00:02:00 
sudo nsenter -t $PIDh3 -n ip link set h3-p1-s2-p1 up 
sudo nsenter -t $PIDs2 -n ip addr add 10.0.3.3 dev s2-p1-h3-p1 
sudo nsenter -t $PIDs2 -n ip link set dev s2-p1-h3-p1 address 00:00:00:00:03:33 
sudo nsenter -t $PIDs2 -n ip link set s2-p1-h3-p1 up 
sudo nsenter -t $PIDh2 -n ip addr add 10.0.1.0 dev h2-p1-s1-p2 
sudo nsenter -t $PIDh2 -n ip link set dev h2-p1-s1-p2 address 00:00:00:00:01:00 
sudo nsenter -t $PIDh2 -n ip link set h2-p1-s1-p2 up 
sudo nsenter -t $PIDs1 -n ip addr add 10.0.2.2 dev s1-p2-h2-p1 
sudo nsenter -t $PIDs1 -n ip link set dev s1-p2-h2-p1 address 00:00:00:00:02:22 
sudo nsenter -t $PIDs1 -n ip link set s1-p2-h2-p1 up 
sudo nsenter -t $PIDh1 -n ip addr add 10.0.1.0 dev h1-p1-s1-p1 
sudo nsenter -t $PIDh1 -n ip link set dev h1-p1-s1-p1 address 00:00:00:00:01:00 
sudo nsenter -t $PIDh1 -n ip link set h1-p1-s1-p1 up 
sudo nsenter -t $PIDs1 -n ip addr add 10.0.1.1 dev s1-p1-h1-p1 
sudo nsenter -t $PIDs1 -n ip link set dev s1-p1-h1-p1 address 00:00:00:00:01:11 
sudo nsenter -t $PIDs1 -n ip link set s1-p1-h1-p1 up 
docker exec h4 ip link set h4-p1-s2-p2 promisc on 
docker exec h4 ethtool -K h4-p1-s2-p2 tx off tx off 
docker exec h3 ip link set h3-p1-s2-p1 promisc on 
docker exec h3 ethtool -K h3-p1-s2-p1 tx off tx off 
docker exec h2 ip link set h2-p1-s1-p2 promisc on 
docker exec h2 ethtool -K h2-p1-s1-p2 tx off tx off 
docker exec h1 ip link set h1-p1-s1-p1 promisc on 
docker exec h1 ethtool -K h1-p1-s1-p1 tx off tx off 

 
 echo "Setting default route for hosts (Check the code for custom routes) " 
 
 
 echo "By default, this script will set the host default gateway to the switch interface connected to the host" 
 #By default, this script will set the host default gateway to the switch interface connected to the host 
#Change this lines to set custon routes 
docker exec s1 route add default gw 10.0.1.1
 docker exec s2 route add default gw 10.0.3.0
 docker exec h4 route add default gw 10.0.2.0
 docker exec h3 route add default gw 10.0.3.3
 docker exec h2 route add default gw 10.0.2.2
 docker exec h1 route add default gw 10.0.1.0
 docker exec s4 sh -c 'echo 0 >> /proc/sys/net/ipv4/ip_forward' 
docker exec s4 sh -c 'nohup simple_switch  --thrift-port 5001  -i 1@s4-p1-s2-p3 -i 2@s4-p2-s1-p4 int.json --log-console >> /tmp/switch.log &' 
docker exec s4 sh -c 'echo "table_add MyIngress.ipv4_lpm ipv4_forward 10.0.1.1/32  => 00:00:00:00:01:00 2" | simple_switch_CLI --thrift-port 5001'  
docker exec s4 sh -c 'echo " table_add MyIngress.ipv4_lpm ipv4_forward 10.0.2.2/32 =>  00:00:00:00:01:00 2" | simple_switch_CLI --thrift-port 5001'  
docker exec s4 sh -c 'echo " table_add MyIngress.ipv4_lpm ipv4_forward 10.0.3.3/32 =>  00:00:00:00:02:00 1" | simple_switch_CLI --thrift-port 5001'  
docker exec s4 sh -c 'echo " table_add MyIngress.ipv4_lpm ipv4_forward 10.0.4.4/32 =>  00:00:00:00:02:00 1" | simple_switch_CLI --thrift-port 5001'  
docker exec s4 sh -c 'echo " table_set_default MyEgress.swtrace add_swtrace 4" | simple_switch_CLI --thrift-port 5001'  
docker exec s1 sh -c 'echo 0 >> /proc/sys/net/ipv4/ip_forward' 
docker exec s1 sh -c 'nohup simple_switch  --thrift-port 5001  -i 1@s1-p1-h1-p1 -i 2@s1-p2-h2-p1 -i 3@s1-p3-s3-p1 -i 4@s1-p4-s4-p2 int.json --log-console >> /tmp/switch.log &' 
docker exec s1 sh -c 'echo "table_add MyIngress.ipv4_lpm ipv4_forward 10.0.1.1/32  => 00:00:00:00:01:11 1" | simple_switch_CLI --thrift-port 5001'  
docker exec s1 sh -c 'echo " table_add MyIngress.ipv4_lpm ipv4_forward 10.0.2.2/32 =>  00:00:00:00:02:22 2" | simple_switch_CLI --thrift-port 5001'  
docker exec s1 sh -c 'echo " table_add MyIngress.ipv4_lpm ipv4_forward 10.0.3.3/32 =>  00:00:00:00:03:00 3" | simple_switch_CLI --thrift-port 5001'  
docker exec s1 sh -c 'echo " table_add MyIngress.ipv4_lpm ipv4_forward 10.0.4.4/32 =>  00:00:00:00:04:00 4" | simple_switch_CLI --thrift-port 5001'  
docker exec s1 sh -c 'echo " table_set_default MyEgress.swtrace add_swtrace 1" | simple_switch_CLI --thrift-port 5001'  
docker exec s2 sh -c 'echo 0 >> /proc/sys/net/ipv4/ip_forward' 
docker exec s2 sh -c 'nohup simple_switch  --thrift-port 5001  -i 1@s2-p1-h3-p1 -i 2@s2-p2-h4-p1 -i 3@s2-p3-s4-p1 -i 4@s2-p4-s3-p2 int.json --log-console >> /tmp/switch.log &' 
docker exec s2 sh -c 'echo "table_add MyIngress.ipv4_lpm ipv4_forward 10.0.1.1/32  => 00:00:00:00:04:00 4" | simple_switch_CLI --thrift-port 5001'  
docker exec s2 sh -c 'echo " table_add MyIngress.ipv4_lpm ipv4_forward 10.0.2.2/32 =>  00:00:00:00:03:00 3" | simple_switch_CLI --thrift-port 5001'  
docker exec s2 sh -c 'echo " table_add MyIngress.ipv4_lpm ipv4_forward 10.0.3.3/32 =>  00:00:00:00:03:33 1" | simple_switch_CLI --thrift-port 5001'  
docker exec s2 sh -c 'echo " table_add MyIngress.ipv4_lpm ipv4_forward 10.0.4.4/32 =>  00:00:00:00:04:44 2" | simple_switch_CLI --thrift-port 5001'  
docker exec s2 sh -c 'echo " table_set_default MyEgress.swtrace add_swtrace 2" | simple_switch_CLI --thrift-port 5001'  
docker exec s3 sh -c 'echo 0 >> /proc/sys/net/ipv4/ip_forward' 
docker exec s3 sh -c 'nohup simple_switch  --thrift-port 5001  -i 1@s3-p1-s1-p3 -i 2@s3-p2-s2-p4 int.json --log-console >> /tmp/switch.log &' 
docker exec s3 sh -c 'echo "table_add MyIngress.ipv4_lpm ipv4_forward 10.0.1.1/32  => 00:00:00:00:01:00 1" | simple_switch_CLI --thrift-port 5001'  
docker exec s3 sh -c 'echo " table_add MyIngress.ipv4_lpm ipv4_forward 10.0.2.2/32 =>  00:00:00:00:01:00 1" | simple_switch_CLI --thrift-port 5001'  
docker exec s3 sh -c 'echo " table_add MyIngress.ipv4_lpm ipv4_forward 10.0.3.3/32 =>  00:00:00:00:02:00 2" | simple_switch_CLI --thrift-port 5001'  
docker exec s3 sh -c 'echo " table_add MyIngress.ipv4_lpm ipv4_forward 10.0.4.4/32 =>  00:00:00:00:02:00 2" | simple_switch_CLI --thrift-port 5001'  
docker exec s3 sh -c 'echo " table_set_default MyEgress.swtrace add_swtrace 3" | simple_switch_CLI --thrift-port 5001'  

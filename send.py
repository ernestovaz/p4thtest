#!/usr/bin/env python3

import argparse
import sys
import socket
import random
import struct
import time  
from string import ascii_uppercase

from scapy.all import Packet, bind_layers, BitField, ShortField, IntField, XByteField, PacketListField, FieldLenField, Raw, Ether, IP, UDP, sendp, get_if_hwaddr,get_if_list, sniff

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface
    
  
class InBandNetworkTelemetry(Packet):
    fields_desc = [ BitField("switchID_t", 0, 31),
                    BitField("ingress_port",0, 9),
                    BitField("egress_port",0, 9),
                    BitField("egress_spec", 0, 9),
                    BitField("ingress_global_timestamp", 0, 48),
                    BitField("egress_global_timestamp", 0, 48),
                    BitField("enq_timestamp",0, 32),
                    BitField("enq_qdepth",0, 19),
                    BitField("deq_timedelta", 0, 32),
                    BitField("deq_qdepth", 0, 19)
                  ]
    def extract_padding(self, p):
                return "", p

class nodeCount(Packet):
  name = "nodeCount"
  fields_desc = [ ShortField("count", 0),
                  PacketListField("INT", [], InBandNetworkTelemetry, count_from=lambda pkt:(pkt.count*1))]


def generate_payload(size):
    return ''.join(random.choice('@%#') for i in range(size))


def main():
    pkts_per_s = float(sys.argv[2])
    s_per_pkts = 1.0 / pkts_per_s

    payload_size = int(sys.argv[3])
    mtu = int(sys.argv[4])

    full_fragments = payload_size // mtu
    full_fragment_size = mtu
    partial_fragment_size = payload_size - (full_fragments * mtu)

    if full_fragments > 0:
        full_payload = generate_payload(full_fragment_size)
    if partial_fragment_size > 0:
        partial_payload = generate_payload(partial_fragment_size)

    if len(sys.argv)<3:
        print('pass 2 arguments: <destination> "<message>"')
        exit(1)
        
    iface = "host1-p1-sw1-p1"
    addr = socket.gethostbyname(sys.argv[1])
    bind_layers(IP, nodeCount, proto = 253)
    if full_fragments > 0:
        full_pkt = (Ether(src=get_if_hwaddr(iface), dst="ff:ff:ff:ff:ff:ff") 
            / IP(dst=addr, proto=253) / nodeCount(count = 0,INT=[])
            / full_payload)
        full_pkt.show2()

    if partial_fragment_size > 0:
        partial_pkt = (Ether(src=get_if_hwaddr(iface), dst="ff:ff:ff:ff:ff:ff") 
            / IP(dst=addr, proto=253) / nodeCount(count = 0,INT=[])
            / partial_payload)
        partial_pkt.show2()


    #sendp(pkt, iface=iface)
    #pkt.show2()
    #hexdump(pkt)
    
    try:
        if full_fragments > 0:
            sendp(full_pkt, iface=iface, inter=s_per_pkts, count=full_fragments)
        if partial_fragment_size > 0:
            sendp(partial_pkt, iface=iface)
    

    except KeyboardInterrupt:
        raise

if __name__ == '__main__':
    main()

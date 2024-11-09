#!/usr/bin/env python3
import argparse
import sys
import socket
import random
import struct
import json

from time import sleep
from scapy.all import Packet, bind_layers, XByteField, FieldLenField, BitField, ShortField, IntField, PacketListField, Ether, IP, TCP, Raw, sendp, get_if_hwaddr, get_if_list, sniff, split_layers

def pkt2dict(pkt):
    packet_dict = {}
    for line in pkt.show2(dump=True).split('\n'):
        if '###' in line:
            if '|###' in line:
                sublayer = line.strip('|#[] ')
                packet_dict[layer][sublayer] = {}
            else:
                layer = line.strip('#[] ')
                packet_dict[layer] = {}
        elif '=' in line:
            if '|' in line and 'sublayer' in locals():
                key, val = line.strip('| ').split('=', 1)
                packet_dict[layer][sublayer][key.strip()] = val.strip('\' ')
            else: 
                key, val = line.split('=', 1)
                val = val.strip('\' ')
                if(val):
                    try:
                        packet_dict[layer][key.strip()] = eval(val)
                    except:
                        packet_dict[layer][key.strip()] = val
        #else:
        #    print("pkt2dict packet not decoded: " + line)
    return packet_dict

def get_if():
    ifs=get_if_list()
    iface=None
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
    """any thing after this packet is extracted is padding"""
    def extract_padding(self, p):
                return "", p

class nodeCount(Packet):
  name = "nodeCount"
  fields_desc = [ ShortField("count", 0),
                  PacketListField("INT", [], InBandNetworkTelemetry, count_from=lambda pkt:(pkt.count*1))]

def remove_raw_padding(packet):
    payload = packet[Raw].load
    if payload[:2] == b'\x00\x00':
        packet[Raw].load = payload[2:]

def handle_pkt(pkt):
    remove_raw_padding(pkt)
    print(json.dumps(pkt2dict(pkt)))
    sys.stdout.flush()


def main():
    bind_layers(IP, nodeCount)
    split_layers(IP, TCP)
    bind_layers(nodeCount, TCP)
    iface = 'host2-p1-sw1-p2'
    sys.stdout.flush()
    sniff(iface = iface,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()

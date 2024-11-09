#!/usr/bin/env python3
from scapy.all import sniff, sendp, IP, TCP, UDP, Raw, Packet, BitField, BitFieldLenField, ShortField, bind_layers, PacketListField
import sys


target_ip = sys.argv[1]


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


bind_layers(TCP, nodeCount)
bind_layers(UDP, nodeCount)


def forward_packet(packet):
    if IP in packet and (TCP in packet or UDP in packet):
        transport_layer = packet[TCP] if TCP in packet else packet[UDP]

        new_packet = (
                packet[IP] /
                transport_layer /
                nodeCount(count=0,INT=[])
        )

        if Raw in packet:
            new_packet = new_packet / packet[Raw].load 

        new_packet[IP].dst = target_ip  # Change the destination IP
        del new_packet[IP].chksum       # Recalculate checksum to avoid issues

        new_packet.show2()
        sendp(new_packet)                   


def main():
    print('Listening...')
    sniff(iface="lo0", prn=forward_packet)


if __name__ == "__main__":
    main()


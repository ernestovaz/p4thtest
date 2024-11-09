#!/usr/bin/env python3

import os
import sys
import subprocess
import time
import argparse
import signal
import json
import re

def main():
    args = commandline_arguments()

    payload_size = calculate_actual_payload_size(args.payload_size, args.unit)
    payload_arguments = f'{args.speed} {payload_size} {args.mtu} '

    hosts = get_hosts(args.file)
    target_address = next(x for x in hosts if x.name == args.TARGET).addresses[0]

    start_time = time.time()

    server_command = f'docker exec {args.TARGET} ./scripts/receive.py'
    client_command = f'docker exec {args.SOURCE} ./scripts/send.py {target_address} {payload_arguments}'
    server = run(server_command)
    client = run(client_command)

    client.wait()
    server.terminate()

    if args.verbose:
        print('[client]')
        print(f'    {client_command}')
        verbose_print(client)
        print()
        print('[server]')
        print(f'    {server_command}')
        verbose_print(server)
    else:
        normal_print(server)

    if args.verbose:
        elapsed_time = time.time() - start_time
        print(f'took {elapsed_time} seconds')
 

class Host:
    def __init__(self, name: str, addresses: list[str]):
        self.name = name
        self.addresses = addresses


def get_hosts(topology_file):
    with open(topology_file) as file:
        topology = json.load(file)
        node_list = topology['elements']['nodes']

        hostnames = [
            node['data']['name']
            for node in node_list
            if node['data']['type'] == 'Host']

        hosts = [
            Host(name, [
                node['data']['ip'].split('/')[0] #TODO: improve this
                for node in node_list
                if node['data']['type'] == 'Port' and node['data']['parent'] == name
            ])

            for name in hostnames]

        return hosts


def commandline_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('SOURCE',
        help='source host for sending the probe',
        type=str)
    parser.add_argument('TARGET',
        help='target host for sending the probe',
        type=str)

    parser.add_argument('-f', '--file', 
        help='topology file for tests, needed if one cannot be found in current directory', 
        type=str, default='topology.json')
    parser.add_argument('-s', '--speed', 
        help='amount of fragments sent per second',
        type=int,  default=5)
    parser.add_argument('-m', '--mtu', 
        help='maximun transmission unit to fragment payload, in bytes (defaults to 1024)', 
        type=int, default=1024)
    parser.add_argument('-p', '--payload-size', 
        help='size of complete payload, default unit is bytes ' +
        '(if payload size is larger than MTU, payload will use fragments of maximum size)', 
        type=int, default=128)
    parser.add_argument('-u', '--unit', 
        help='unit for payload size', 
        choices=['B', 'KB', 'MB', 'GB'], 
        type=str.upper, default='B')

    parser.add_argument('-v', '--verbose', 
        action='store_true')

    return parser.parse_args()

# UTILS

def verbose_print(process):
    for line in process.stdout:
        print(f'    {line.decode()}', end='')
    print()
    for line in process.stderr:
        print(f'    {line.decode()}', end='')

def normal_print(process):
    for line in process.stdout:
        print(f'{line.decode()}', end='')
    for line in process.stderr:
        print(f'{line.decode()}', end='')



def calculate_actual_payload_size(raw_size, unit):
    unit_multiplier = {
        'B' : 1,
        'KB' : 1024,
        'MB' : 1024**2,
        'GB' : 1024**3
    }
    actual_size = raw_size * unit_multiplier[unit]
    return actual_size
    

def run(command):
    process = subprocess.Popen(
        command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    return process


if __name__ == '__main__':
    main()

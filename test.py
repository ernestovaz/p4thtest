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
    result = {}
    result['errors'] = []

    args = commandline_arguments(result)

    payload_size = calculate_actual_payload_size(args.payload_size, args.unit)
    payload_arguments = f'{args.speed} {payload_size} {args.mtu} '

    hosts = get_hosts(args.file)
    if args.verbose:
        for x in hosts: print(x)

    target_address = next(x for x in hosts if x.name == args.TARGET).address

    start_time = time.time()

    server_command = f'docker exec {args.TARGET} ./scripts/receive.py'
    client_command = f'docker exec {args.SOURCE} ./scripts/send.py {target_address} {payload_arguments}'
    stats_command  = 'docker stats --no-stream --format json'
    server = run(server_command)
    client = run(client_command)
    stats  = run(stats_command)

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
        read_data(server, result)

    elapsed_time = time.time() - start_time
    result['duration'] = elapsed_time

    stats.wait()
    parse_stats(stats, result)

    print(json.dumps(result))


class Host:
    def __init__(self, name: str, address: str):
        self.name = name
        self.address = address
    def __str__(self):
        return json.dumps({'name': self.name, 'address':self.address})


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
            ][0])
            for name in hostnames]
        return hosts


def commandline_arguments(metadata_dict):
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

    args = parser.parse_args()

    metadata_dict['source'] = args.SOURCE
    metadata_dict['target'] = args.TARGET
    metadata_dict['speed'] = args.speed
    metadata_dict['mtu'] = args.mtu
    metadata_dict['payload_size'] = args.payload_size
    metadata_dict['unit'] = args.unit

    return args


# UTILS


def verbose_print(process):
    for line in process.stdout:
        print(f'    {line.decode()}', end='')
    print()
    for line in process.stderr:
        print(f'    {line.decode()}', end='')


def read_data(process, result):
    errors = process.stderr.read().decode('utf-8')
    output = process.stdout.read().decode('utf-8')

    if errors:
        add_error_data(result, 'target_host_error', errors)

    try: 
        data = json.loads(output)
        result['received_packet'] = data
    except json.JSONDecodeError as e:
        result['received_packet'] = {}
        add_error_data(result, 'json_decode_error', f'[{e}]: server returned [{output}]')

        
def parse_stats(process, result):
    stats = {}
    for line in process.stdout:
        container = json.loads(line)
        stats[container['Name']] = {
                'processes':    container['PIDs'],
                'network_io':   container['NetIO'],
                'memory_usage': container['MemPerc'],
                'cpu_usage':    container['CPUPerc']
        }
    result['container_metrics'] = stats


def add_error_data(result_dict, error_type, message):
    errors = result_dict['errors']
    errors.append({
        'type': error_type,
        'message': message
    })
    result_dict['errors'] = errors


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

import os
import sys
import subprocess
import time
import argparse
import signal
import json
import re

from pyspin.spin import make_spin, Default
 
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


@make_spin(Default, "Running...")
def wait(process):
    process.wait()


def pretty_print(process):
    for line in process.stdout:
        print(line.decode(), end='')

def run_scream(command):
    process = subprocess.Popen(
        command.split(),
        stderr=subprocess.PIPE)
    return process

def run(command):
    process = subprocess.Popen(
        command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    return process


def main():
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

    args = parser.parse_args()
    multiplier = {
        'B' : 1,
        'KB' : 1024,
        'MB' : 1024**2,
        'GB' : 1024**3
    }
    arguments = f'{args.speed} {args.payload_size*multiplier[args.unit]} {args.mtu} '

    hosts = get_hosts()

    #target_address = next(x for x in hosts if x.name == args.TARGET).addresses[0]
    #TODO: improve

    start_time = time.time()
    #server = run(f'docker exec {args.TARGET} /scripts/receive.py')
    #client = run(f'docker exec {args.SOURCE} /scripts/send.py {target_address} {arguments}')
    client = run(f'docker exec {args.SOURCE} /scripts/send.py 10.0.4.4 {arguments}')
    print(f'docker exec {args.SOURCE} /scripts/send.py 10.0.4.4 {arguments}')

    wait(client)
    #server.terminate()

    pretty_print(client)

    elapsed_time = time.time() - start_time

    print(f'Took {elapsed_time} seconds.')


if __name__ == '__main__':
    main()

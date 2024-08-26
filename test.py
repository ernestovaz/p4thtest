#! /usr/bin/env python3
import os
import sys
import subprocess
import time
import argparse
import signal

from pyspin.spin import make_spin, Default


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

    start_time = time.time()
    server = run_scream('docker exec host2 /scripts/receive.py')
    client = run(f'docker exec host1 /scripts/send.py 10.0.2.2 {arguments}')
    wait(client)
    elapsed_time = time.time() - start_time

    server.terminate()

    print(f'Took {elapsed_time} seconds.')


if __name__ == '__main__':
    main()

import os

input_filename='input.txt'

def do_action(action: str, from_host: str, to_host: str):
    command = ''
    if action == 'ping':
        command = f'docker exec -ti {from_host} ping {to_host}'
    else if action == 'flood'
        command = f'docker exec -ti {from_host} "iperf -c {to_host} -t 200 -l 1200 -P 6"'

    os.popen(command)


def main():
    with open(input_filename) as input:
        for line in input:
            first_host, action, second_host = line.split()
            do_action(action, first_host, second_host)


if __name__ == '__main__':
    main()

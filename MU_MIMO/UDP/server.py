import socket
import sys
import time
import os
from scapy.layers.inet import IP,UDP, send

__author__ = 'uriklarman'

chunk_size = 2**12 # 4KB chunks
big_file_name = '/Users/uriklarman/Professional/MCMH.zip'


def run_server(num_clients=2, server_ip='10.49.32.127', port=1609):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Bind the socket to the port
        server_address = (server_ip, port)
        print >>sys.stderr, 'starting up on %s port %s' % server_address
        sock.bind(server_address)

        file_size = str(os.path.getsize(big_file_name))
        clients = []
        for i in range(num_clients):
            print >>sys.stderr, '\nwaiting to receive message'
            data, address = sock.recvfrom(chunk_size)
            clients.append(address)

            print >>sys.stderr, 'received %s from %s' % (data, address)
            print >>sys.stderr, data

            sent = sock.sendto(file_size, address)
            print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)

        time.sleep(1)

        # send_file_over_socket(sock, clients)
        send_garbage_over_scapy(clients)

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()


def send_file_over_socket(sock, clients):
    amount_sent = 0
    next_print = 100
    with open(big_file_name, 'r') as f:
        while True:
            time.sleep(0.0001)
            chunk = f.read(chunk_size)
            if not chunk:
                print >>sys.stderr, 'amount_sent: %s MB' % (amount_sent / (2**20))
                break

            for client in clients:
                sock.sendto(chunk, client)
            amount_sent += len(chunk)
            if amount_sent > next_print:
                print >>sys.stderr, 'amount_sent: %s MB' % (amount_sent / (2**20))
                next_print += 2**20 * 100

def send_garbage_over_scapy(clients):
    for client in clients:
        ip_pkt = IP(dst=client[0])/UDP(dport=client[1])
        send(ip_pkt)
    print 'done'


if __name__ == "__main__":
    run_server(server_ip='localhost', num_clients=1)
    # run_server(num_clients=1)
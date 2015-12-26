import socket
from random import choice, randint
from socket import AF_INET,SOCK_DGRAM,SOL_SOCKET,SO_REUSEADDR,SO_BROADCAST
import sys
import os
from time import sleep

from MU_MIMO.testbed.client import create_socket_for_local_ip, SERVER_PORT, SERVER_IP

__author__ = 'uriklarman'


def run_server(num_clients=10, server_ip=SERVER_IP, port=SERVER_PORT):
	sock = create_socket_for_local_ip(port, server_ip)
	clients = []
	try:
		for i in range(num_clients):
			print >>sys.stderr, '\nwaiting to receive message'
			data, address = sock.recvfrom(65535)
			clients.append(address)
			print 'received %s from %s' % (data, address)

			# sent = sock.sendto('Accepted', address)
			# print >>sys.stderr, 'sent %s bytes back to %s' % (sent, address)


		while True:
			data_len = randint(60000, 65000)
			data = bytearray(os.urandom(data_len))
			sock.sendto(data,choice(clients))
			sleep(0.001)

	finally:
		print 'closing socket ', sock.getsockname()
		sock.close()

def send_garbage_over_scapy(clients):
		for client in clients:
				ip_pkt = IP(dst=client[0])/UDP(dport=client[1])
				send(ip_pkt)
		print 'done'


if __name__ == "__main__":
	run_server(num_clients=1)
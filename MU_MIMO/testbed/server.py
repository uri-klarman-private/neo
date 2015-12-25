import socket
from random import choice, randint
from socket import AF_INET,SOCK_DGRAM,SOL_SOCKET,SO_REUSEADDR,SO_BROADCAST
import sys
import os
from time import sleep

__author__ = 'uriklarman'


CLIENT_PORT = 1609
BROADCASTER_PORT = 1610
SERVER_PORT = 1611


def create_socket_for_local_ip(port, local_ip=None):
	if not local_ip:
		# local_ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
		local_ip = ''
	sock = socket.socket(AF_INET, SOCK_DGRAM)
	try:
		sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		sock.bind((local_ip, port))
		sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		return sock
	except:
			print 'closing socket ', sock.getsockname()
			sock.close()
			raise


def run_server(num_clients=10, server_ip='10.49.32.127', port=SERVER_PORT):
	sock = create_socket_for_local_ip(port=port)
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
from random import choice, randint
import sys
import os
from time import sleep

from MU_MIMO.testbed.client import create_socket_for_local_ip, SERVER_PORT, SERVER_IP, CLIENT_PORT

__author__ = 'uriklarman'


def run_server(num_clients=10, port=SERVER_PORT):
	sock = create_socket_for_local_ip(port,ip=SERVER_IP)
	clients = []
	try:
		for i in range(num_clients):
			print >>sys.stderr, '\nwaiting to receive message'
			data, address = sock.recvfrom(65535)
			print 'received %s from %s' % (data, address)
			if address[1] == CLIENT_PORT:
				if address not in clients:
					clients.append(address)
				sock.sendto('OK',choice(clients))


		while True:
			data_len = randint(8500, 9200) # OS X USB/ethernet max size: 9216 bytes
			# data_len = randint(2000, 2250) # according to fragmantation level of linksys EA8500
			data = bytearray(os.urandom(data_len))
			sock.sendto(data,choice(clients))
			# sleep(0.001)

	finally:
		print 'closing socket ', sock.getsockname()
		sock.close()


if __name__ == "__main__":
	run_server(num_clients=2)
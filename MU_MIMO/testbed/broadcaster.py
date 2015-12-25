import os
from socket import AF_INET,SOCK_DGRAM,SOL_SOCKET,SO_REUSEADDR,SO_BROADCAST
import socket
import sys
from time import sleep

from MU_MIMO.testbed.client import create_socket_for_local_ip, BROADCASTER_PORT, CLIENT_PORT


def start_broadcast():
	sock = create_socket_for_local_ip(port=BROADCASTER_PORT)
	try:
		garbage = '_' + bytearray(os.urandom(1450))
		packet_index = 0
		while(True):
			sock.sendto(str(packet_index).zfill(19) + garbage, ('255.255.255.255', CLIENT_PORT))
			sleep(0.02)

			if data == sys.maxint:
				data = 0
			else:
				data += 1
	finally:
		print 'closing socket ', sock.getsockname()
		sock.close()


if __name__ == '__main__':
	start_broadcast()


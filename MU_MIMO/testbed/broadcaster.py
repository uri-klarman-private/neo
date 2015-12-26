import os
from socket import AF_INET,SOCK_DGRAM,SOL_SOCKET,SO_REUSEADDR,SO_BROADCAST
import socket
import sys
from time import sleep
from datetime import datetime

from MU_MIMO.testbed.client import create_socket_for_local_ip, BROADCASTER_PORT, CLIENT_PORT


def start_broadcast():
	sock = create_socket_for_local_ip(port=BROADCASTER_PORT)
	try:
		garbage = '_' + bytearray(os.urandom(1450))
		packet_index = 0
		while(True):
			sock.sendto(str(packet_index).zfill(19) + garbage, ('255.255.255.255', CLIENT_PORT))
			# sleep(0.001)

			if packet_index == sys.maxint:
				packet_index = 0
			else:
				packet_index += 1
				if packet_index % 100000 == 0:
					print '%s %s broadcasts sent ' % (datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f"), packet_index)
	finally:
		print 'closing socket ', sock.getsockname()
		sock.close()


if __name__ == '__main__':
	start_broadcast()


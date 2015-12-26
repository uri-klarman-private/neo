import os
import socket
from socket import AF_INET,SOCK_DGRAM,SOL_SOCKET,SO_REUSEADDR,SO_BROADCAST
import datetime
from netifaces import interfaces, ifaddresses, AF_INET

__author__ = 'uriklarman'


CLIENT_PORT = 1609
BROADCASTER_PORT = 1610
SERVER_PORT = 1611
SERVER_IP = '192.168.1.108'


def create_socket_for_local_ip(port, ip=''):
	sock = socket.socket(AF_INET, SOCK_DGRAM)
	try:
		if not ip:
			ip = socket.gethostbyname(socket.gethostname())
		sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		sock.bind((ip, port))
		sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		print 'created socket ', sock.getsockname()
		return sock
	except:
			print 'closing socket ', sock.getsockname()
			sock.close()
			raise


def run_client(server_ip, port=CLIENT_PORT):
	sock = create_socket_for_local_ip(port)
	try:
		while True:
			sent = sock.sendto('client:' + sock.getsockname()[0], (server_ip, SERVER_PORT))
			data, server = sock.recvfrom(65535)
			if data == 'OK':
				path =os.path.join('results', 'client_%s_%s.log' % (datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f"),
				                                                    sock.getsockname()[0]))
				filename = os.path.abspath(path)
		with open(filename, "w", 1000) as f:
			while True:
				data, sender = sock.recvfrom(65535)
				if sender[1] == SERVER_PORT:
					f.write('%s,%s,%s,\n'%(datetime.datetime.now(), sender[1], len(data)))
				else:
					f.write('%s,%s,%s,%s\n'%(datetime.datetime.now(), sender[1], len(data), data[:19]))

	finally:
		print 'closing socket ', sock.getsockname()
		sock.close()


if __name__ == "__main__":
	run_client(SERVER_IP)

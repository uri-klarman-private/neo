import os
import socket
from socket import AF_INET,SOCK_DGRAM,SOL_SOCKET,SO_REUSEADDR,SO_BROADCAST
import datetime

__author__ = 'uriklarman'


CLIENT_PORT = 1609
BROADCASTER_PORT = 1610
SERVER_PORT = 1611


def create_socket_for_local_ip(port, local_ip=None):
	if not local_ip:
		# local_ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
		# local_ip = ''
		# see options here: http://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
		local_ip = socket.gethostbyname(socket.gethostname())
	sock = socket.socket(AF_INET, SOCK_DGRAM)
	try:
		sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		sock.bind((local_ip, port))
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
		sent = sock.sendto('client!', (server_ip, SERVER_PORT))
		data, server = sock.recvfrom(65535)
		filename = os.path.abspath(os.path.join('results', 'client_%s_%s.log' % (str(datetime.datetime.now()).replace(':', '_'), sock.getsockname()[0])))
		with open(filename, "w", 1000) as f:
			while True:
				data, sender = sock.recvfrom(65535)
				f.write('%s,%s,%s,%s\n'%(datetime.datetime.now(), sender[1], len(data), data[:19]))




	finally:
		print 'closing socket ', sock.getsockname()
		sock.close()

if __name__ == "__main__":
	server_ip = '192.168.1.112'
	run_client(server_ip)

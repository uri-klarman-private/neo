from socket import AF_INET,SOCK_DGRAM,SOL_SOCKET,SO_REUSEADDR,SO_BROADCAST
import socket
import sys
from time import sleep

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


def start_broadcast():
	sock = create_socket_for_local_ip(port=BROADCASTER_PORT)
	try:
		data = 0
		while(True):
			sock.sendto(str(data)+'x'*1000, ('255.255.255.255', CLIENT_PORT))
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


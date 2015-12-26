import os
import socket
from socket import AF_INET,SOCK_DGRAM,SOL_SOCKET,SO_REUSEADDR,SO_BROADCAST
import datetime
from netifaces import interfaces, ifaddresses, AF_INET

__author__ = 'uriklarman'


CLIENT_PORT = 1609
BROADCASTER_PORT = 1610
SERVER_PORT = 1611
SERVER_IP = '192.168.1.147'


def create_socket_for_local_ip(port, local_ip=None, wifi_ip=True):
	if not local_ip:
		all_ips = ip4_addresses()
		local_ip = [ip for ip in all_ips if ('192.168.1' in ip) == wifi_ip][0]
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


def ip4_addresses():
	ip_list = []
	for interface in interfaces():
		for link in ifaddresses(interface).get(AF_INET, ()):
			if 'broadcast' in link:
				ip_list.append(link['addr'])
	return ip_list


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
	run_client(SERVER_IP)

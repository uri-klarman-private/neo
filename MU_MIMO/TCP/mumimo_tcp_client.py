import socket
import sys
import datetime

__author__ = 'uriklarman'

max_data = 2**27 # 1GB file
chunk_size = 2**24 # 16MB chunks


def run_client(port=1609, server_ip='192.168.1.49'):
    try:
        # Create a TCP/IP socket
        sock = socket.create_connection((server_ip, port))

        # Send data
        message = 'GO!'
        print >>sys.stderr, 'sending "%s"' % message
        sock.sendall(message)
        file_size = int(sock.recv(chunk_size))


        receive_file(sock, file_size)
        # receive_file(sock, file_size)

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()


def receive_file(sock, file_size):
    # first Iteration takes start_time
    data = sock.recv(chunk_size)
    start_time = datetime.datetime.now()
    amount_received = len(data)
    next_print = 0
    while amount_received < file_size:
        data = sock.recv(chunk_size)
        amount_received += len(data)
        if amount_received > next_print:
            print >>sys.stderr, 'amount received: %s MB' % (amount_received / (2**20))
            next_print += 2**20 * 100

    end_time = datetime.datetime.now()
    print >>sys.stderr, 'amount received: %s MB' % (amount_received / (2**20))
    print >>sys.stderr, 'total time: %s' % (end_time - start_time)


if __name__ == "__main__":
    # run_client(server_ip='localhost')
    run_client()
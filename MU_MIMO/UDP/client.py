import socket
import sys
import datetime

__author__ = 'uriklarman'

max_data = 2**27 # 1GB file
chunk_size = 2**12 # 4K chunks


def run_client(server_ip='10.49.32.127', port=1609):
    try:
        server_address = (server_ip, port)

        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Send data
        message = 'GO!'
        print >>sys.stderr, 'sending "%s"' % message
        sent = sock.sendto(message, server_address)

        data, server = sock.recvfrom(chunk_size)
        file_size = int(data)

        receive_file(sock, file_size)

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()


def receive_file(sock, file_size):
    # first Iteration takes start_time
    data, server = sock.recvfrom(chunk_size)
    start_time = datetime.datetime.now()
    amount_received = len(data)
    next_print = 0
    while amount_received < file_size:
        data, server = sock.recvfrom(chunk_size)
        amount_received += len(data)
        if amount_received > next_print:
            print >>sys.stderr, 'amount received: %s MB' % (amount_received / (2**20))
            next_print += 2**20 * 100

    end_time = datetime.datetime.now()
    print >>sys.stderr, 'amount received: %s MB' % (amount_received / (2**20))
    print >>sys.stderr, 'total time: %s' % (end_time - start_time)


if __name__ == "__main__":
    run_client(server_ip='localhost')
    # run_client()
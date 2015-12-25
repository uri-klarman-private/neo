import socket
import sys
import time
import os
import multiprocessing

__author__ = 'uriklarman'

chunk_size = 2**19 # 512KB chunks
big_file_name = '/Users/uriklarman/Professional/MCMH.zip'


def run_server(num_clients=2, port=1609, server_ip='192.168.1.49'):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = (server_ip, port)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(num_clients)
    connections = []
    clients_address = []

    file_size = str(os.path.getsize(big_file_name))

    try:
        while len(connections) < num_clients:
            # Wait for a connection
            print >>sys.stderr, 'waiting for a connection'
            conn, address = sock.accept()
            connections.append(conn)
            clients_address.append(address)
            print >>sys.stderr, 'connection from', address
            data = conn.recv(chunk_size)
            print >>sys.stderr, 'received "%s"' % data
            conn.sendall(file_size)

        # Send file to each connection, serially
        # for conn in connections:
        #     send_file([conn])
        #     time.sleep(5)

        # Send file to each connection in parallel
        send_file(connections)

        # jobs = []
        # for conn in connections:
        #     job = multiprocessing.Process(target=send_file, args=(conn,))
        #     jobs.append(job)
        #
        # for job in jobs:
        #     job.start()
        #
        # for job in jobs:
        #     job.join()


    finally:
        time.sleep(10)
        print >>sys.stderr, 'cleaning up connections'
        # Clean up the connections
        for conn in connections:
            conn.close()
        print >>sys.stderr, 'closing socket'
        sock.close()


def send_file(connections):
    amount_sent = 0
    next_print = 100
    with open(big_file_name, 'r') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                print >>sys.stderr, 'amount_sent: %s MB' % (amount_sent / (2**20))
                break

            for conn in connections:
                conn.sendall(chunk)
            amount_sent += len(chunk)
            if amount_sent > next_print:
                print >>sys.stderr, 'amount_sent: %s MB' % (amount_sent / (2**20))
                next_print += 2**20 * 100


if __name__ == "__main__":
    # run_server(ip='localhost', num_clients=2)
    run_server(num_clients=2)
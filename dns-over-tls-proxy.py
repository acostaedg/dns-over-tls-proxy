#!/usr/bin/env python

import os
import ssl
import socket
import logging
import multiprocessing
import socketserver

NAMESERVER = os.environ['NAMESERVER']
NAMESERVER_PORT = os.environ['NAMESERVER_PORT']
DNS_PROXY_ADDR = '0.0.0.0'
DNS_PROXY_PORT = 30853
BUFFER_SIZE = 1024

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

def tlsWrapper(data, hostname, port=NAMESERVER_PORT) -> bytes:
    NameserverAddress = (hostname, port)
    ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    with socket.create_connection(NameserverAddress, timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname=hostname) as TLSsocket:
            TLSsocket.send(data)
            result = TLSsocket.recv(BUFFER_SIZE)
            return result


class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        """ self.request is the TCP socket connected to the client """
        logging.info('TCP connection from %s', self.client_address)
        self.data = self.request.recv(BUFFER_SIZE)
        result = tlsWrapper(self.data, NAMESERVER)
        self.request.send(result)


class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        """
        This class works similar to the TCP handler class, except that
        self.request consists of a pair of data and client socket, and since
        there is no connection the client address must be given explicitly
        when sending data back via sendto().
        """
        logging.info('UDP connection from %s', self.client_address)
        data, socket = self.request
        data = bytes([00]) + bytes([len(data)]) + data
        tls_answer = tlsWrapper(data, hostname=NAMESERVER)
        udp_answer = tls_answer[2:]
        socket.sendto(udp_answer, self.client_address)


def main() -> None:
    ProxyServerAddress = (DNS_PROXY_ADDR, DNS_PROXY_PORT)
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    socketserver.ThreadingUDPServer.allow_reuse_address = True    

    # TCP DNS proxy server instance
    TCPServerInstance = socketserver.ThreadingTCPServer(ProxyServerAddress, TCPHandler)

    # UDP DNS proxy server instance
    UDPServerInstance = socketserver.ThreadingUDPServer(ProxyServerAddress, UDPHandler)

    # Running both TCP and UDP servers in separate processes simultaneously
    process1 = multiprocessing.Process(target=TCPServerInstance.serve_forever)
    process2 = multiprocessing.Process(target=UDPServerInstance.serve_forever)

    # Starting both processes
    process1.start()
    logging.info('DNS TCP Proxy server started and listening on port %s', DNS_PROXY_PORT)

    process2.start()
    logging.info('DNS UDP Proxy started and listening on port %s', DNS_PROXY_PORT)

if __name__ == '__main__':
    main()

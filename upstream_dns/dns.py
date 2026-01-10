 # -*- coding: UTF-8 -*-

from dnslib import *
import gevent
from gevent.server import DatagramServer
from gevent import socket
from random import randint
from time import sleep

always_respond_ip = '1.2.3.4'



class DNSServer(DatagramServer):

    def handle_dns_request(self, data, address):
        #print(data, flush = True)
        req = DNSRecord.parse(data)
        qname = str(req.q.qname)
        qid = req.header.id

        response = DNSRecord(DNSHeader(qr=1, aa=1, ra=1),
                                     q=DNSQuestion(qname),
                                     a=RR(qname, rdata=A(always_respond_ip)))

        response.header.id = qid

        # forward request to real upstream dns recursive resolver
        sock = socket.socket(type=socket.SOCK_DGRAM)
        sock.connect(("1.1.1.1", 53))
        sock.send(data)
        response_data = sock.recv(2048)
        # print(response_data, flush=True)
        # print(DNSRecord.parse(response_data))
        # print(response_data, flush=True)


        #response_data = response.pack()
        print(response_data, flush=True)

        # exagerated delay to demonstrate PoC
        sleep(1.5)

        self.socket.sendto(response_data, address)
            

    def handle(self, data, address):
        print("in", flush=True)
        self.handle_dns_request(data, address)
        print("out", flush=True)

def main():
    DNSServer(':53').serve_forever()


if __name__ == '__main__':
    main()

 # -*- coding: UTF-8 -*-

import dnslib
import gevent
from gevent.server import DatagramServer
from gevent import socket
from random import randint
from threading import Lock

ns = '10.0.0.5'


class Cache:
    def __init__(self):
        self.list = {}

    def get(self, key):
        return self.list.get(key, None)

    def set(self, key, value):
        self.list[key] = value

cache = Cache()


class DNSServer(DatagramServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print("setuping", flush=True)
        self.upstream_sock = socket.socket(type=socket.SOCK_DGRAM)
        self.upstream_lock = Lock()

        address = (ns, 53)
        self.upstream_sock.bind(('10.0.0.2', 22222))
        self.upstream_sock.connect(address)
        print("done", flush=True)

    def handle_dns_request(self, data, address):

        req = dnslib.DNSRecord.parse(data)
        qname = str(req.q.qname)
        qid = req.header.id
        cache_key = (qname, req.q.qtype, req.q.qclass)
        print(cache_key)

        record = cache.get(cache_key)
        print(cache_key, record)
        if record:

            response = dnslib.DNSRecord.parse(record)
            response.header.id = qid
            self.socket.sendto(response.pack(), address)

        else:

            request = dnslib.DNSRecord.parse(data)

            # weak qID range for PoC validity
            qid_to_request = randint(10000, 10500)
            request.header.id = qid_to_request

            self.upstream_sock.send(request.pack())

            dns_response, dns_address = self.upstream_sock.recvfrom(8192)
            response = dnslib.DNSRecord.parse(dns_response)

            while response.header.id != qid_to_request:
                dns_response, dns_address = self.upstream_sock.recvfrom(8192)
                #print("recv", flush=True)
                response = dnslib.DNSRecord.parse(dns_response)

            if response.header.id == qid_to_request:
                qname = str(response.q.qname)
                cache.set(cache_key, dns_response)
                response.header.id = qid
                print("match", response)
                self.socket.sendto(response.pack(), address)
            else:
                print("qid diff", response.header.id, qid_to_request, flush=True)

    def handle(self, data, address):
        with self.upstream_lock:
            print("in", flush=True)
            self.handle_dns_request(data, address)
            print("out", flush=True)

def main():
    DNSServer('10.0.0.2:53').serve_forever()


if __name__ == '__main__':
    main()

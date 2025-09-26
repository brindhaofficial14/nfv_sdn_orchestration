from scapy.all import sniff, IP, send
from prometheus_client import start_http_server, Counter
from datetime import datetime
import os

# Setup logging
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
os.makedirs(LOG_DIR, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOG_DIR, f"nat_{timestamp}.log")

CONFIG_FILE = os.path.join(CONFIG_DIR, "nat_config.txt")
 

def get_current_nat_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            parts = f.read().strip().split(";")
            snat_ip = parts[0] if len(parts) > 0 and parts[0] else None
            dnat_ip = parts[1] if len(parts) > 1 and parts[1] else None
            return snat_ip, dnat_ip
    return None, None




def log_message(msg):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - {msg}\n")

# Prometheus metrics
nat_packets = Counter('nat_packets_total', 'Total packets handled by NAT')
tcp_packets = Counter('nat_tcp_total', 'Total TCP packets rewritten by NAT')
udp_packets = Counter('nat_udp_total', 'Total UDP packets rewritten by NAT')
icmp_packets = Counter('nat_icmp_total', 'Total ICMP packets rewritten by NAT')

start_http_server(9102)

def handle_packet(pkt):
    if IP in pkt:
        nat_packets.inc()
        original_src = pkt[IP].src
        original_dst = pkt[IP].dst

        snat_ip, dnat_ip = get_current_nat_config()
        if snat_ip:
            pkt[IP].src = snat_ip
        

        if dnat_ip:
            pkt[IP].dst = dnat_ip
        

        # Track protocol-specific stats
        proto = pkt[IP].proto
        if proto == 6:
            tcp_packets.inc()
        elif proto == 17:
            udp_packets.inc()
        elif proto == 1:
            icmp_packets.inc()

        log_message(f"[NAT] Rewrote src {original_src} → {pkt[IP].src}, dst {original_dst} → {pkt[IP].dst}")

        # Recalculate checksums if needed (Scapy usually handles it)
        del pkt[IP].chksum

        # Forward the modified packet
        send(pkt)

if __name__ == "__main__":
    log_message("🌐 NAT VNF with forwarding & protocol tracking started on port 9102")
    sniff(prn=handle_packet, store=0)

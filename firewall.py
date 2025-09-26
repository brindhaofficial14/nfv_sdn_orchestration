from scapy.all import sniff, IP
from prometheus_client import Counter, start_http_server
from datetime import datetime
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOG_DIR, f"firewall_{timestamp}.log")
BLOCKED_IPS_FILE = os.path.join(CONFIG_DIR, "firewall_blocked_ips.txt")

def log_message(msg):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - {msg}\n")

packets_processed = Counter("fw_packets_total", "Packets processed")
start_http_server(9100)



def get_blocked_ips():
    if os.path.exists(BLOCKED_IPS_FILE):
        with open(BLOCKED_IPS_FILE, "r") as f:
            return [ip.strip() for ip in f.read().split(";") if ip.strip()]
    return []


def block_packet(pkt):
    if IP in pkt:
        packets_processed.inc()
        blocked_ips = get_blocked_ips()
        src_ip = pkt[IP].src
        if src_ip in blocked_ips:
            log_message(f"[FIREWALL] Blocked packet from {src_ip}")
        else:
            log_message(f"[FIREWALL] Allowed: {src_ip} → {pkt[IP].dst}")


if __name__ == "__main__":
    log_message("🔥 Firewall VNF started and listening for traffic...")
    sniff(prn=block_packet, store=0)

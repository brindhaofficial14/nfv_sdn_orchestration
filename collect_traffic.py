# collect_traffic.py — Run this manually to collect and label data
from scapy.all import sniff, IP
import csv

OUTPUT_FILE = "traffic.csv"

with open(OUTPUT_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["length", "proto", "ttl", "label"])  # Include label column

    def log(pkt):
        try:
            if IP in pkt:
                # Replace "benign" with actual label as needed ("attack" or "benign")
                writer.writerow([len(pkt), pkt[IP].proto, pkt[IP].ttl, "benign"])
        except Exception as e:
            print(f"Packet logging error: {e}")

    print("📡 Sniffing packets... (press Ctrl+C to stop)")
    sniff(prn=log, count=1000)

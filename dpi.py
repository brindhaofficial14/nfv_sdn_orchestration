from scapy.all import sniff, IP, TCP, Raw
from prometheus_client import start_http_server, Counter
from datetime import datetime
import os
import joblib

# Setup logging
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOG_DIR, f"dpi_{timestamp}.log")

def log_message(msg):
    print(msg)
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - {msg}\n")

# Prometheus metrics
dpi_packets = Counter('dpi_packets_total', 'Total packets inspected by DPI')
dpi_http_detected = Counter('dpi_http_requests_total', 'Total HTTP requests detected by DPI')
dpi_blocked = Counter('dpi_blocked_packets_total', 'Total malicious packets blocked by DPI')
start_http_server(9101)

# Load ML classifier
try:
    model = joblib.load("classifier.pkl")
    log_message("✅ ML classifier loaded successfully.")
except Exception as e:
    model = None
    log_message(f"⚠️ Failed to load classifier: {e}")

# Load HTTP methods allowed by config
def load_allowed_methods():
    methods_file = os.path.join(LOG_DIR, "allowed_methods.txt")
    if os.path.exists(methods_file):
        with open(methods_file, "r") as f:
            return [m.strip().upper() for m in f.readlines() if m.strip()]
    return []

def inspect_packet(pkt):
    if IP in pkt:
        dpi_packets.inc()
        ip_src = pkt[IP].src
        ip_dst = pkt[IP].dst

        # ML classification
        if model:
            try:
                features = [[len(pkt), pkt[IP].proto, pkt[IP].ttl]]
                prediction = model.predict(features)[0]
                if prediction == "attack":
                    log_message(f"⚠️ [DPI] Blocked suspicious packet (ML): {ip_src} → {ip_dst}")
                    dpi_blocked.inc()
                    return
                else:
                    log_message(f"✅ [DPI] Allowed benign packet (ML): {ip_src} → {ip_dst}")
            except Exception as e:
                log_message(f"[DPI] ML classification error: {e}")
        else:
            log_message(f"[DPI] IP packet: {ip_src} → {ip_dst}")

        # HTTP Detection
        if TCP in pkt and pkt[TCP].dport == 80 and Raw in pkt:
            payload = pkt[Raw].load.decode(errors='ignore')
            dpi_http_detected.inc()

            try:
                payload = pkt[Raw].load.decode(errors='ignore')
                if "HTTP" in payload:
                    method = payload.split(" ")[0].upper()
                    allowed_methods = load_allowed_methods()
                    log_message(f"[DPI] HTTP Method Detected: {method}")

                    if method not in allowed_methods:
                        log_message(f"🚫 [DPI] Blocked disallowed HTTP method: {method} from {ip_src}")
                        dpi_blocked.inc()
                        return
                    else:
                        log_message(f" [DPI] Allowed HTTP {method} from {ip_src} → {ip_dst}")
                        dpi_http_detected.inc()
            except Exception as e:
                log_message(f"[DPI] Error parsing HTTP packet: {e}")

if __name__ == "__main__":
    log_message("🔎 DPI VNF with ML & HTTP method filtering started on port 9101")
    sniff(prn=inspect_packet, store=0)

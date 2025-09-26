import os
import time

def check_process(vnf_name):
    try:
        result = os.popen(f"pgrep -f {vnf_name}").read()
        return bool(result.strip())
    except:
        return False

if __name__ == "__main__":
    while True:
        for vnf in ['firewall', 'dpi', 'nat']:
            status = check_process(vnf)
            print(f"[MONITOR] {vnf} status: {'UP' if status else 'DOWN'}")
        time.sleep(5)

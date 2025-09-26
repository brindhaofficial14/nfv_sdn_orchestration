from flask import Flask, jsonify, request, render_template
import os
import time
from datetime import datetime
import requests
import subprocess
from odl_api import add_flow

app = Flask(__name__)

# Base and logs directory inside project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure logs/ exists
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")

# Path to VNF scripts
VNF_SCRIPTS = {
    "firewall": "firewall.py",
    "dpi": "dpi.py",
    "nat": "nat.py"
}
def kill_vnf_ports(ports):
    for port in ports:
        try:
            # Get PID(s) listening on the port
            pid_output = subprocess.check_output(
            ["lsof", "-t", f"-i:{port}"], stderr=subprocess.DEVNULL
            ).decode().strip()
            if pid_output:
                pids = pid_output.splitlines()
                for pid in pids:
                    subprocess.run(["kill", "-9", pid])
                    print(f"✅ Killed process {pid} on port {port}")
            else:
                print(f"ℹ️ No process found on port {port}")
        except subprocess.CalledProcessError:
            print(f"⚠️ lsof failed or no process found on port {port}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/vnf/<vnf>/<action>", methods=["POST"])
def vnf_control(vnf, action):
    kill_vnf_ports(["9100", "9101", "9102"])
    print(f"VNF: {vnf} and Action: {action}")

    if vnf not in VNF_SCRIPTS or action not in ["deploy", "update", "delete"]:
        return jsonify({"message": "Invalid VNF or Action"}), 400
      
    node_id = "openflow:1"

    # Default flow config for deploy
    flow_config = {
        "firewall": {
            "flow_id": "1",
            "match": {"ipv4-source": "10.0.0.1/32"},
            "actions": [{"order": 0, "output-action": {"output-node-connector": "NORMAL"}}]
        },
        "dpi": {
            "flow_id": "2",
            "match": {"ipv4-source": "10.0.0.1/32"},
            "actions": [{"order": 0, "output-action": {"output-node-connector": "3"}}]
        },
        "nat": {
            "flow_id": "3",
            "match": {"ipv4-source": "10.0.0.1/32"},
            "actions": [{"order": 0, "output-action": {"output-node-connector": "4"}}]
        }
    }

    script = VNF_SCRIPTS[vnf]   
    
    if action == "deploy":
        # Create a new timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logfile = os.path.join(LOG_DIR, f"{vnf}_{timestamp}.log")
        

        cfg = flow_config[vnf]
        add_flow(node_id, cfg["flow_id"], cfg["match"], cfg["actions"])

        # 4. Launch the VNF script in background
        venv_python = os.path.join(BASE_DIR, "venv/bin/python")
        subprocess.Popen([venv_python, script], stdout=open(logfile, "w"), stderr=subprocess.STDOUT)
        # msg = vnf.upper() + " flow rule deployed"
        # with open(logfile, "a") as f:
         #    f.write(f"{datetime.now()} - {msg}\n")
        return jsonify({"status": f"{vnf.upper()} flow rule deployed"})

    elif action == "delete":
        flow_id = flow_config[vnf]["flow_id"]
        url = f"http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/{node_id}/table/0/flow/{flow_id}"
        res = requests.delete(url, auth=('admin', 'admin'))
        # Kill the VNF process
        subprocess.call(["pkill", "-f", script])

        return jsonify({"status": f"{vnf.upper()} flow rule deleted", "code": res.status_code})

    elif action == "update":
        # Accept custom flow config from UI/POST
        data = request.json
        print(data)
        new_match = data.get("match")
        new_actions = data.get("actions")

        
        if vnf == "nat":
            # Optional: Custom SNAT and DNAT IPs
            snat_ip = data.get("snat_ip")
            dnat_ip = data.get("dnat_ip")
            nat_config_path = os.path.join(CONFIG_DIR, "nat_config.txt")
            with open(nat_config_path, "w") as f:
                f.write(f"{snat_ip};{dnat_ip}")  # Delimited format
        elif vnf == "firewall":
            blocked_ips = data.get("blocked_ips")
            ip_config_path = os.path.join(CONFIG_DIR, "firewall_blocked_ips.txt")
            with open(ip_config_path, "w") as f:
                f.write(blocked_ips)
        elif vnf == "dpi":
            methods = data.get("allowed_methods", "")
            method_config_path = os.path.join(CONFIG_DIR, "dpi_allowed_methods.txt")
            with open(method_config_path, "w") as f:
                f.write("\n".join(methods.strip().split(";")))
       
        return jsonify({
            "status": f"{vnf.upper()} flow rule updated",
            "new_match": new_match,
            "new_actions": new_actions
        }), 200

    return jsonify({"message": "Unsupported action"}), 400
def get_logfilepath(vnf):
    # List all files in logs/
    files = os.listdir(LOG_DIR)

    # Filter those that start with vnf_ and end with .log
    vnf_logs = [f for f in files if f.startswith(f"{vnf}_") and f.endswith(".log")]

    if not vnf_logs:
        return f"No logs found for {vnf}", 404

    # Sort by filename to get the latest one (timestamp in name helps)
    latest_log_file = sorted(vnf_logs)[-1]
    log_path = os.path.join(LOG_DIR, latest_log_file)
    return log_path

@app.route("/logs/<vnf>")
def get_logs(vnf):
    
    log_path = get_logfilepath(vnf)
    if not log_path.startswith("No logs"):
        with open(log_path, "r") as f:
            return f.read(), 200

@app.route("/deploy_chain", methods=["POST"])
def deploy_chain():
    kill_vnf_ports(["9100", "9101", "9102"])
    log_file = os.path.join(LOG_DIR, f"deploy-chain_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    flows = [
        {"id": "10", "in_port": "1", "out_port": "2"},  # h1 → firewall
        {"id": "11", "in_port": "2", "out_port": "3"},  # firewall → dpi
        {"id": "12", "in_port": "3", "out_port": "4"},  # dpi → nat
        {"id": "13", "in_port": "4", "out_port": "5"},  # nat → h2
    ]

    with open(log_file, "w") as f:
        for flow in flows:
            match = {"in-port": flow["in_port"]}
            actions = [{"order": 0, "output-action": {"output-node-connector": flow["out_port"]}}]
            add_flow("openflow:1", flow["id"], match, actions)
            f.write(f"{datetime.now()} - Flow {flow['id']} added: {flow['in_port']} → {flow['out_port']}\n")

    return jsonify({"status": "Service chain flow rules deployed"}), 200


if __name__ == "__main__":
    app.run(port=5000)

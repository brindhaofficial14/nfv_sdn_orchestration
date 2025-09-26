import requests
import json

BASE_URL = "http://localhost:8181/restconf"
AUTH = ('admin', 'admin')
HEADERS = {'Content-Type': 'application/json'}

def add_flow(node_id, flow_id, match, actions):
    url = f"{BASE_URL}/config/opendaylight-inventory:nodes/node/{node_id}/table/0/flow/{flow_id}"
    flow_data = {
        "flow": [{
            "id": flow_id,
            "table_id": 0,
            "priority": 100,
            "match": match,
            "instructions": {
                "instruction": [{
                    "order": 0,
                    "apply-actions": {
                        "action": actions
                    }
                }]
            }
        }]
    }
    response = requests.put(url, auth=AUTH, headers=HEADERS, data=json.dumps(flow_data))
    print(f"[ODL] Flow {flow_id} added: {response.status_code}")

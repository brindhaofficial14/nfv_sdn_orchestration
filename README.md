# NFV Orchestration using SDN

## Overview
This project demonstrates how VNFs like Firewall, DPI, and NAT can be orchestrated dynamically using SDN (OpenDaylight) and deployed in a virtual network (Mininet).This project builds a lightweight NFV Orchestrator
with the concepts of Software Defined Networking (SDN). The
implementation of the orchestrator is with Flask, Mininet, OpenDaylight (ODL) and Prometheus/Grafana. Virtualized Network
Functions (VNFs) like Firewall, Deep Packet Inspection (DPI)
and Network Address Translation (NAT) will be instantiated,
modified and destroyed in real-time via RESTful API calls.
This project aims to achieve service chaining, AI-based traffic
classification and real-time statistics monitoring in a SDN-based
virtual environment.

## How to Run

```bash
./run_demo.sh
```

## API

- `POST /deploy` – Deploys firewall VNF and sets ODL flow

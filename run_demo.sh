#!/bin/bash
function cleanup() {
echo ""
echo "🧹 Cleaning up NFV processes..."
sudo lsof -t -i:5000 | xargs -r sudo kill -9
sudo lsof -t -i:9100 | xargs -r sudo kill -9
sudo lsof -t -i:9101 | xargs -r sudo kill -9
sudo lsof -t -i:9102 | xargs -r sudo kill -9
sleep 2
pkill -f custom_topo.py
pkill -f orchestrator.py
pkill -f firewall.py
pkill -f dpi.py
pkill -f nat.py
sudo mn -c
echo "✅ All processes terminated."
exit 0
}
trap cleanup SIGINT

echo "Clean up to start fresh..."
cleanup &
sleep 5

echo "Starting Mininet..."                                                                                                                                                                                                                                                                              
sudo python3 custom_topo.py & 
sleep 5

#echo "📡 Starting traffic capture (venv)..."
#sudo ./venv/bin/python collect_traffic.py & 
#sleep 3

#echo "✅ Traffic collection complete. Starting model training..."
#sudo ./venv/bin/python train_classifier.py & 
#sleep 3

echo "Starting Orchestrator..."                                                                                                                                                                                                                                                                                     
sudo ./venv/bin/python orchestrator.py &
sleep 2


#echo "Starting Firewall VNF..."
#sudo ./venv/bin/python firewall.py &
#sleep 2

#echo "Starting DPI VNF.."
#sudo ./venv/bin/python dpi.py &
#sleep 2

#echo "Starting NAT VNF..."
#sudo ./venv/bin/python nat.py &

#echo " All components are running."
echo " Press Ctrl+C to stop and clean up."
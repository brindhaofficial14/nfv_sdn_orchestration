#3.1. Collect Packet Data

#modify VNF (e.g., dpi.py) to save packet features:

from scapy.all import sniff
import csv

with open("traffic.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["length", "proto", "ttl"])
def log(pkt):
    try:
        writer.writerow([len(pkt), pkt.proto, pkt.ttl])
    except: pass
    sniff(prn=log, count=1000)


#3.2. Train ML Model (scikit-learn)

from sklearn.ensemble import RandomForestClassifier
import pandas as pd, joblib

df = pd.read_csv("traffic.csv")
df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
print(df.columns)  # Debug print

if "label" in df.columns:
    y = df["label"]
else:
    raise ValueError("Column 'label' not found in the dataset.")

X = df[["length", "proto", "ttl"]]
y = df["label"]
model = RandomForestClassifier().fit(X, y)
joblib.dump(model, "classifier.pkl")


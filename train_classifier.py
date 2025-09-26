# train_classifier.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

df = pd.read_csv("traffic.csv")                                                                                                                                                                                                 
df.columns = df.columns.str.strip()

if "label" not in df.columns:
    raise ValueError("❌ 'label' column missing in traffic.csv")

X = df[["length", "proto", "ttl"]]
y = df["label"]

model = RandomForestClassifier()
model.fit(X, y)

joblib.dump(model, "classifier.pkl")
print("✅ Model trained and saved as classifier.pkl")

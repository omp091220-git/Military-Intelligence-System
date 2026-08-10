"""
Run this ONCE before using the Attack Prediction page:
    python train_attack_model.py

It reads data/globalterrorism.csv and saves 3 files into models/:
    - attack_prediction_model.pkl
    - target_encoder.pkl
    - feature_encoders.pkl
"""

import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

os.makedirs("models", exist_ok=True)

print("Loading dataset...")
df = pd.read_csv("data/globalterrorism.csv", encoding="latin1", low_memory=False)
print("Rows loaded:", df.shape)

features = [
    "country_txt", "region_txt", "weaptype1_txt", "targtype1_txt",
    "gname", "success", "suicide", "nkill", "nwound",
]
target = "attacktype1_txt"

df = df[features + [target]].dropna()
print("Rows after cleaning:", df.shape)

encoders = {}
for col in ["country_txt", "region_txt", "weaptype1_txt", "targtype1_txt", "gname"]:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

target_encoder = LabelEncoder()
df[target] = target_encoder.fit_transform(df[target])

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training model...")
model = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

pred = model.predict(X_test)
print("\nAccuracy:", accuracy_score(y_test, pred))
print("\nClassification Report:\n", classification_report(y_test, pred))

joblib.dump(model, "models/attack_prediction_model.pkl")
joblib.dump(target_encoder, "models/target_encoder.pkl")
joblib.dump(encoders, "models/feature_encoders.pkl")

print("\nSaved model files into models/ — you can now open the Attack Prediction page.")

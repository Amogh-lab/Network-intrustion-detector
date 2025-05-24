
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder

file_path = "combined_output.csv"
df = pd.read_csv(file_path)

df.columns = df.columns.str.strip()
df = df.drop(columns=['Flow ID', 'Source IP', 'Destination IP', 'Timestamp'], errors='ignore')
df = df.replace([np.inf, -np.inf], np.nan).dropna()

label_encoder = LabelEncoder()
df['Label'] = label_encoder.fit_transform(df['Label'])

X = df.drop(columns=['Label'])
y = df['Label']

model = joblib.load("random_forest_cicids2017.joblib")

feature_columns = X.columns.tolist()

labels = [
    'BENIGN', 
    'DDoS', 
    'DoS GoldenEye', 
    'DoS Hulk', 
    'DoS Slowhttptest',
    'DoS slowloris', 
    'Heartbleed', 
    'PortScan', 
    'Web Attack – Brute Force',
    'Web Attack – Sql Injection', 
    'Web Attack – XSS'
]

dummy_input = np.array([[80, 39537833, 2, 0, 0, 0, 0, 0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0.0, 0.050584462, 39500000.0, 0.0, 39500000, 39500000, 39500000, 39500000.0, 0.0, 39500000, 39500000, 0, 0.0, 0.0, 0, 0, 0, 0, 0, 0, 64, 0, 0.050584462, 0.0, 0, 0, 0.0, 0.0, 0.0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0.0, 0.0, 0.0, 64, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 296, -1, 0, 32, 0.0, 0.0, 0, 0, 39500000.0, 0.0, 39500000, 39500000]])

assert dummy_input.shape[1] == len(feature_columns), f"Feature count mismatch! dummy input has {dummy_input.shape[1]}, expected {len(feature_columns)}"

dummy_df = pd.DataFrame(dummy_input, columns=feature_columns)

prediction = model.predict(dummy_df)[0]

predicted_label = labels[prediction]

print("Prediction:", predicted_label)

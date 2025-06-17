
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

dummy_input = np.array([[80, 105693351, 15, 3, 5720, 6, 520, 0, 381.3333333, 238.0236083, 6, 0, 2, 3.464101615, 54.17559332, 0.170303996, 6217255.941, 13200000, 52400000, 69, 106000000, 7549520.143, 14200000, 52400000, 480, 105000000, 52300000, 29500000, 73200000, 31500000, 0, 0, 0, 0, 496, 100, 0.141919996, 0.028383999, 0, 520, 301.3684211, 263.3966613, 69377.80117, 0, 0, 0, 1, 0, 0, 0, 0, 0, 318.1111111, 381.3333333, 2, 496, 0, 0, 0, 0, 0, 0, 15, 5720, 3, 6, 29200, 0, 11, 32, 3767384, 5327188.34, 7534275, 493, 19600000, 19300000, 52400000, 5339405]])

assert dummy_input.shape[1] == len(feature_columns), f"Feature count mismatch! dummy input has {dummy_input.shape[1]}, expected {len(feature_columns)}"

dummy_df = pd.DataFrame(dummy_input, columns=feature_columns)

prediction = model.predict(dummy_df)[0]

predicted_label = labels[prediction]

print("Prediction:", predicted_label)

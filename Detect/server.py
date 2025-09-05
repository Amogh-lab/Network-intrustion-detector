import numpy as np
import pandas as pd
import joblib
import requests
import time
from flask import Flask, jsonify
from flask import request
import streamlit as st
from datetime import datetime

app = Flask(__name__)

feature_columns = [
    'Destination Port', 'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
    'Total Length of Fwd Packets', 'Total Length of Bwd Packets', 'Fwd Packet Length Max',
    'Fwd Packet Length Min', 'Fwd Packet Length Mean', 'Fwd Packet Length Std',
    'Bwd Packet Length Max', 'Bwd Packet Length Min', 'Bwd Packet Length Mean',
    'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean',
    'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min', 'Fwd IAT Total', 'Fwd IAT Mean',
    'Fwd IAT Std', 'Fwd IAT Max', 'Fwd IAT Min', 'Bwd IAT Total', 'Bwd IAT Mean',
    'Bwd IAT Std', 'Bwd IAT Max', 'Bwd IAT Min', 'Fwd PSH Flags', 'Bwd PSH Flags',
    'Fwd URG Flags', 'Bwd URG Flags', 'Fwd Header Length', 'Bwd Header Length',
    'Fwd Packets/s', 'Bwd Packets/s', 'Min Packet Length', 'Max Packet Length',
    'Packet Length Mean', 'Packet Length Std', 'Packet Length Variance',
    'FIN Flag Count', 'SYN Flag Count', 'RST Flag Count', 'PSH Flag Count',
    'ACK Flag Count', 'URG Flag Count', 'CWE Flag Count', 'ECE Flag Count',
    'Down/Up Ratio', 'Average Packet Size', 'Avg Fwd Segment Size',
    'Avg Bwd Segment Size', 'Fwd Header Length.1', 'Fwd Avg Bytes/Bulk',
    'Fwd Avg Packets/Bulk', 'Fwd Avg Bulk Rate', 'Bwd Avg Bytes/Bulk',
    'Bwd Avg Packets/Bulk', 'Bwd Avg Bulk Rate', 'Subflow Fwd Packets',
    'Subflow Fwd Bytes', 'Subflow Bwd Packets', 'Subflow Bwd Bytes',
    'Init_Win_bytes_forward', 'Init_Win_bytes_backward', 'act_data_pkt_fwd',
    'min_seg_size_forward', 'Active Mean', 'Active Std', 'Active Max',
    'Active Min', 'Idle Mean', 'Idle Std', 'Idle Max', 'Idle Min'
]

labels = [
    'BENIGN', 'DDoS', 'DoS GoldenEye', 'DoS Hulk', 'DoS Slowhttptest',
    'DoS slowloris', 'Heartbleed', 'PortScan',
    'Web Attack – Brute Force', 'Web Attack – Sql Injection', 'Web Attack – XSS'
]

model = joblib.load("random_forest_cicids2017.joblib")

if 'results' not in st.session_state:
    st.session_state.results = []

# Streamlit layout
st.title("Real-Time Port-Based Intrusion Detection Dashboard")

placeholder = st.empty()

# Function to make predictions
def fetch_and_predict():
    try:
        start_res = requests.post('http://127.0.0.1:5000/start-capture')
        time.sleep(10)
        stop_res = requests.post('http://127.0.0.1:5000/stop-capture')
        flows = stop_res.json()

        new_results = []
        for flow in flows:
            row = [flow.get(col, 0) for col in feature_columns]
            df = pd.DataFrame([row], columns=feature_columns)
            prediction = model.predict(df)[0]
            port = flow.get('Destination Port', 0)
            new_results.append({"port": port, "state": labels[prediction]})

        return new_results

    except Exception as e:
        st.error(f"Error: {e}")
        return []

# Stream live updates
auto_run = st.checkbox("Auto Refresh Every 10 Seconds", value=True)
if st.button("Run Once"):
    st.session_state.results = fetch_and_predict()

if auto_run:
    while True:
        st.session_state.results = fetch_and_predict()
        df = pd.DataFrame(st.session_state.results)
        with placeholder.container():
            st.subheader("Prediction Results")
            st.dataframe(df)
        time.sleep(10)
else:
    df = pd.DataFrame(st.session_state.results)
    st.subheader("Prediction Results")
    st.dataframe(df)

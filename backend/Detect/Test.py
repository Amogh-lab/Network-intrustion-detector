import numpy as np
import pandas as pd
import joblib
import requests
import time
from flask import Flask, jsonify

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

def periodic_prediction():
    while True:
        try:
            # Start the capture
            print("\n Starting packet capture...")
            start_res = requests.post('http://127.0.0.1:5000/start-capture')
            print(" Start response:", start_res.json())

            # Wait for 10 seconds
            time.sleep(10)

            # Stop the capture and get flows
            print(" Stopping capture and fetching flows...")
            stop_res = requests.post('http://127.0.0.1:5000/stop-capture')
            flows = stop_res.json()

            results = []
            for flow in flows:
                row = [flow.get(col, 0) for col in feature_columns]
                df = pd.DataFrame([row], columns=feature_columns)
                prediction = model.predict(df)[0]
                port = flow.get('Destination Port', 0)
                results.append({"port": port, "state": labels[prediction]})

            print(" Prediction result:", results)

        except Exception as e:
            print(" Error during periodic prediction:", e)

        time.sleep(2) 


if __name__ == '__main__':
    import threading
    threading.Thread(target=periodic_prediction, daemon=True).start()
    app.run(port=6000, debug=True)
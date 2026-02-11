import numpy as np
import os
import pandas as pd
import joblib
from flask import Flask, jsonify
from scapy.all import sniff, IP, TCP
import threading, time, uuid
from flask_cors import CORS
from datetime import datetime
import psutil  # NEW: to map ports → applications

# --- Flask app setup ---
app = Flask(__name__)
CORS(app)  # allow React frontend to fetch

# --- Global variables ---
flows = {}
capture_thread = None
stop_event = threading.Event()
BULK_TIMEOUT = 1.0  # seconds

# --- Load ML model ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), "random_forest_cicids2017.joblib")
model = joblib.load(MODEL_PATH)

# --- Labels & feature columns ---
labels = [
    'BENIGN', 'DDoS', 'DoS GoldenEye', 'DoS Hulk', 'DoS Slowhttptest',
    'DoS slowloris', 'Heartbleed', 'PortScan',
    'Web Attack – Brute Force', 'Web Attack – Sql Injection', 'Web Attack – XSS'
]

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

# ----------------- Capture Logic -----------------

def get_flow_key(pkt):
    ip = pkt[IP]
    tcp = pkt[TCP]
    return (ip.src, ip.dst, tcp.sport, tcp.dport)

def init_flow():
    return {
        "flow_id": str(uuid.uuid4()),
        "start_time": None,
        "end_time": None,
        "fwd": {"pkt_lengths": [], "iat": [], "count": 0, "last_ts": None, "bulk_bytes":0, "bulk_count":0, "bulk_rate":0, "bulk_start":None, "header_lengths":[], "psh":0, "urg":0},
        "bwd": {"pkt_lengths": [], "iat": [], "count": 0, "last_ts": None, "bulk_bytes":0, "bulk_count":0, "bulk_rate":0, "bulk_start":None, "header_lengths":[], "psh":0, "urg":0},
        "packet_times": [], "packet_lengths": [],
        "flags": {"FIN":0,"SYN":0,"RST":0,"PSH":0,"ACK":0,"URG":0,"CWE":0,"ECE":0},
        "init_win_bytes_fwd": None, "init_win_bytes_bwd": None,
        "act_data_pkt_fwd": 0, "min_seg_size_fwd": None
    }

def handle_bulk(flow, direction, ts, length):
    side = flow[direction]
    if side["bulk_start"] is None or ts - side["bulk_start"] > BULK_TIMEOUT:
        side["bulk_start"] = ts
        side["bulk_bytes"] = 0
        side["bulk_count"] = 0
    side["bulk_bytes"] += length
    side["bulk_count"] += 1
    side["bulk_rate"] = side["bulk_bytes"] / (ts - side["bulk_start"] + 0.00001)

def packet_handler(pkt):
    if IP in pkt and TCP in pkt:
        ts = time.time()
        ip, tcp = pkt[IP], pkt[TCP]
        key = get_flow_key(pkt)
        rev_key = (key[1], key[0], key[3], key[2])
        direction = "fwd" if key in flows else "bwd"
        flow = flows[key] if direction=="fwd" else flows.get(rev_key, init_flow())

        if direction=="fwd" and key not in flows: flows[key] = flow
        elif direction=="bwd" and rev_key not in flows: flows[rev_key] = flow

        if flow["start_time"] is None: flow["start_time"] = ts
        flow["end_time"] = ts

        side = flow[direction]
        side["count"] += 1
        length = len(pkt)
        flow["packet_lengths"].append(length)
        flow["packet_times"].append(ts)
        side["pkt_lengths"].append(length)
        if side["last_ts"] is not None:
            side["iat"].append(ts - side["last_ts"])
        side["last_ts"] = ts
        side["header_lengths"].append(tcp.dataofs * 4)
        if tcp.flags & 0x08: side["psh"] += 1
        if tcp.flags & 0x20: side["urg"] += 1

        if direction=="fwd":
            flow["init_win_bytes_fwd"] = tcp.window
            flow["min_seg_size_fwd"] = tcp.dataofs*4 if flow["min_seg_size_fwd"] is None else min(flow["min_seg_size_fwd"], tcp.dataofs*4)
            if len(tcp.payload) > 0: flow["act_data_pkt_fwd"] += 1
        else:
            flow["init_win_bytes_bwd"] = tcp.window

        handle_bulk(flow, direction, ts, length)

def safe_stat(func, data):
    try:
        return func(data) if len(data) > 0 else 0
    except:
        return 0

def get_flow_features(flow, key):
    """Return dict for React table including ML prediction"""
    duration = flow["end_time"] - flow["start_time"] if flow["end_time"] and flow["start_time"] else 1
    fwd, bwd = flow["fwd"], flow["bwd"]

    # Build feature row for ML
    row = [flow.get(col,0) for col in feature_columns]
    df = pd.DataFrame([row], columns=feature_columns)
    pred_label = labels[ model.predict(df)[0] ]

    return {
        "time": datetime.now().strftime("%H:%M:%S"),
        "port": key[3],
        "attack": pred_label
    }

# ----------------- New: Port → Service Mapping -----------------
def get_ports_services():
    """Return list of active ports with corresponding process/service name"""
    port_mapping = []
    connections = psutil.net_connections(kind='inet')
    seen_ports = set()
    
    for conn in connections:
        if conn.laddr and conn.laddr.port not in seen_ports:
            seen_ports.add(conn.laddr.port)
            try:
                proc = psutil.Process(conn.pid)
                name = proc.name()
            except:
                name = "Unknown"
            port_mapping.append({"port": conn.laddr.port, "service": name})
    return port_mapping

# ----------------- Flask Endpoints -----------------
@app.route("/live-data", methods=["GET"])
def live_data():
    """Capture packets for 2 seconds and return ML predictions for React"""
    global flows, capture_thread, stop_event
    stop_event.clear()
    flows.clear()

    # Start capture in a separate thread
    capture_thread = threading.Thread(target=lambda: sniff(prn=packet_handler, stop_filter=lambda _: stop_event.is_set()))
    capture_thread.start()

    # Capture for 2 seconds
    time.sleep(2)
    stop_event.set()
    capture_thread.join()

    # Return JSON for React
    return jsonify([get_flow_features(flow,key) for key, flow in flows.items()])

@app.route("/ports-services", methods=["GET"])
def ports_services():
    """Return active ports and the process/service name"""
    return jsonify(get_ports_services())

# ----------------- Run App -----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # In cloud environments (Render, Heroku), we might not have permission to sniff packets.
    # We'll try to start the sniffer, but if it fails, we'll log it and continue so the web server still runs.
    try:
        # Start capture thread if permissions allow
        # (Note: In many PaaS like Render, this might still fail or yield no packets)
        pass 
    except Exception as e:
        print(f"Warning: Could not start sniffer or permissions issue: {e}")

    app.run(host="0.0.0.0", port=port, debug=False)

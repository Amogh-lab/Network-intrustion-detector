from flask import Flask, jsonify, request
from scapy.all import sniff, IP, TCP
from collections import defaultdict
import threading
import time
import uuid
import statistics

app = Flask(__name__)
flows = {}
capture_thread = None
stop_event = threading.Event()

# === BULK logic settings ===
BULK_TIMEOUT = 1.0  # seconds

def get_flow_key(pkt):
    ip = pkt[IP]
    tcp = pkt[TCP]
    return (ip.src, ip.dst, tcp.sport, tcp.dport)

def init_flow():
    return {
        "flow_id": str(uuid.uuid4()),
        "start_time": None,
        "end_time": None,

        "fwd": {
            "pkt_lengths": [],
            "iat": [],
            "count": 0,
            "last_ts": None,
            "bulk_bytes": 0,
            "bulk_count": 0,
            "bulk_rate": 0,
            "bulk_start": None,
            "header_lengths": [],
            "psh": 0,
            "urg": 0
        },
        "bwd": {
            "pkt_lengths": [],
            "iat": [],
            "count": 0,
            "last_ts": None,
            "bulk_bytes": 0,
            "bulk_count": 0,
            "bulk_rate": 0,
            "bulk_start": None,
            "header_lengths": [],
            "psh": 0,
            "urg": 0
        },
        "packet_times": [],
        "packet_lengths": [],
        "flags": {
            "FIN": 0, "SYN": 0, "RST": 0, "PSH": 0, "ACK": 0, "URG": 0, "CWE": 0, "ECE": 0
        },
        "init_win_bytes_fwd": None,
        "init_win_bytes_bwd": None,
        "act_data_pkt_fwd": 0,
        "min_seg_size_fwd": None,
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
        ip = pkt[IP]
        tcp = pkt[TCP]
        key = get_flow_key(pkt)
        rev_key = (key[1], key[0], key[3], key[2])

        direction = "fwd" if key in flows else "bwd"
        if direction == "fwd":
            if key not in flows:
                flows[key] = init_flow()
            flow = flows[key]
        else:
            if rev_key not in flows:
                flows[rev_key] = init_flow()
            flow = flows[rev_key]

        if flow["start_time"] is None:
            flow["start_time"] = ts
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

        # TCP header length
        side["header_lengths"].append(tcp.dataofs * 4)

        # PSH/URG flags
        if tcp.flags & 0x08:
            side["psh"] += 1
        if tcp.flags & 0x20:
            side["urg"] += 1

        # TCP Flag counts
        flags = tcp.flags
        for f, bit in zip(["FIN", "SYN", "RST", "PSH", "ACK", "URG", "CWE", "ECE"],
                          [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]):
            if flags & bit:
                flow["flags"][f] += 1

        if direction == "fwd":
            flow["init_win_bytes_fwd"] = tcp.window
            flow["min_seg_size_fwd"] = tcp.dataofs * 4 if flow["min_seg_size_fwd"] is None else min(flow["min_seg_size_fwd"], tcp.dataofs * 4)
            if len(tcp.payload) > 0:
                flow["act_data_pkt_fwd"] += 1
        else:
            flow["init_win_bytes_bwd"] = tcp.window

        handle_bulk(flow, direction, ts, length)

def safe_stat(func, data):
    try:
        return func(data) if len(data) > 0 else 0
    except:
        return 0

def get_flow_features(flow, key):
    duration = flow["end_time"] - flow["start_time"]
    fwd, bwd = flow["fwd"], flow["bwd"]
    total_pkts = fwd["count"] + bwd["count"]
    total_bytes = sum(fwd["pkt_lengths"]) + sum(bwd["pkt_lengths"])

    inter_arrival = [j - i for i, j in zip(flow["packet_times"][:-1], flow["packet_times"][1:])]
    idle_times = []
    if len(flow["packet_times"]) > 1:
        for i in range(1, len(flow["packet_times"])):
            gap = flow["packet_times"][i] - flow["packet_times"][i-1]
            if gap > 1.0:
                idle_times.append(gap)

    return {
        "Destination Port": key[3],
        "Flow Duration": duration,
        "Total Fwd Packets": fwd["count"],
        "Total Backward Packets": bwd["count"],
        "Total Length of Fwd Packets": sum(fwd["pkt_lengths"]),
        "Total Length of Bwd Packets": sum(bwd["pkt_lengths"]),
        "Fwd Packet Length Max": safe_stat(max, fwd["pkt_lengths"]),
        "Fwd Packet Length Min": safe_stat(min, fwd["pkt_lengths"]),
        "Fwd Packet Length Mean": safe_stat(statistics.mean, fwd["pkt_lengths"]),
        "Fwd Packet Length Std": safe_stat(statistics.stdev, fwd["pkt_lengths"]),
        "Bwd Packet Length Max": safe_stat(max, bwd["pkt_lengths"]),
        "Bwd Packet Length Min": safe_stat(min, bwd["pkt_lengths"]),
        "Bwd Packet Length Mean": safe_stat(statistics.mean, bwd["pkt_lengths"]),
        "Bwd Packet Length Std": safe_stat(statistics.stdev, bwd["pkt_lengths"]),
        "Flow Bytes/s": total_bytes / duration if duration > 0 else 0,
        "Flow Packets/s": total_pkts / duration if duration > 0 else 0,
        "Flow IAT Mean": safe_stat(statistics.mean, inter_arrival),
        "Flow IAT Std": safe_stat(statistics.stdev, inter_arrival),
        "Flow IAT Max": safe_stat(max, inter_arrival),
        "Flow IAT Min": safe_stat(min, inter_arrival),

        "Fwd IAT Total": sum(fwd["iat"]),
        "Fwd IAT Mean": safe_stat(statistics.mean, fwd["iat"]),
        "Fwd IAT Std": safe_stat(statistics.stdev, fwd["iat"]),
        "Fwd IAT Max": safe_stat(max, fwd["iat"]),
        "Fwd IAT Min": safe_stat(min, fwd["iat"]),

        "Bwd IAT Total": sum(bwd["iat"]),
        "Bwd IAT Mean": safe_stat(statistics.mean, bwd["iat"]),
        "Bwd IAT Std": safe_stat(statistics.stdev, bwd["iat"]),
        "Bwd IAT Max": safe_stat(max, bwd["iat"]),
        "Bwd IAT Min": safe_stat(min, bwd["iat"]),

        "Fwd PSH Flags": fwd["psh"],
        "Bwd PSH Flags": bwd["psh"],
        "Fwd URG Flags": fwd["urg"],
        "Bwd URG Flags": bwd["urg"],
        "Fwd Header Length": sum(fwd["header_lengths"]),
        "Bwd Header Length": sum(bwd["header_lengths"]),
        "Fwd Packets/s": fwd["count"] / duration if duration > 0 else 0,
        "Bwd Packets/s": bwd["count"] / duration if duration > 0 else 0,
        "Min Packet Length": safe_stat(min, flow["packet_lengths"]),
        "Max Packet Length": safe_stat(max, flow["packet_lengths"]),
        "Packet Length Mean": safe_stat(statistics.mean, flow["packet_lengths"]),
        "Packet Length Std": safe_stat(statistics.stdev, flow["packet_lengths"]),
        "Packet Length Variance": safe_stat(statistics.variance, flow["packet_lengths"]),

        **flow["flags"],

        "Down/Up Ratio": bwd["count"] / fwd["count"] if fwd["count"] > 0 else 0,
        "Average Packet Size": total_bytes / total_pkts if total_pkts > 0 else 0,
        "Avg Fwd Segment Size": safe_stat(statistics.mean, fwd["pkt_lengths"]),
        "Avg Bwd Segment Size": safe_stat(statistics.mean, bwd["pkt_lengths"]),
        "Fwd Header Length.1": sum(fwd["header_lengths"]),

        "Fwd Avg Bytes/Bulk": fwd["bulk_bytes"],
        "Fwd Avg Packets/Bulk": fwd["bulk_count"],
        "Fwd Avg Bulk Rate": fwd["bulk_rate"],
        "Bwd Avg Bytes/Bulk": bwd["bulk_bytes"],
        "Bwd Avg Packets/Bulk": bwd["bulk_count"],
        "Bwd Avg Bulk Rate": bwd["bulk_rate"],

        "Subflow Fwd Packets": fwd["count"],
        "Subflow Fwd Bytes": sum(fwd["pkt_lengths"]),
        "Subflow Bwd Packets": bwd["count"],
        "Subflow Bwd Bytes": sum(bwd["pkt_lengths"]),

        "Init_Win_bytes_forward": flow["init_win_bytes_fwd"] or 0,
        "Init_Win_bytes_backward": flow["init_win_bytes_bwd"] or 0,
        "act_data_pkt_fwd": flow["act_data_pkt_fwd"],
        "min_seg_size_forward": flow["min_seg_size_fwd"] or 0,

        "Active Mean": safe_stat(statistics.mean, inter_arrival),
        "Active Std": safe_stat(statistics.stdev, inter_arrival),
        "Active Max": safe_stat(max, inter_arrival),
        "Active Min": safe_stat(min, inter_arrival),

        "Idle Mean": safe_stat(statistics.mean, idle_times),
        "Idle Std": safe_stat(statistics.stdev, idle_times),
        "Idle Max": safe_stat(max, idle_times),
        "Idle Min": safe_stat(min, idle_times),
    }

@app.route('/start-capture', methods=['POST'])
def start_capture():
    global capture_thread, flows
    stop_event.clear()
    flows.clear()
    capture_thread = threading.Thread(target=lambda: sniff(prn=packet_handler, stop_filter=lambda _: stop_event.is_set()))
    capture_thread.start()
    return jsonify({"status": "Capture started"})

@app.route('/stop-capture', methods=['POST'])
def stop_capture():
    stop_event.set()
    capture_thread.join()
    return jsonify([
        get_flow_features(flow, key)
        for key, flow in flows.items()
    ])

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, jsonify, request
from scapy.all import sniff, IP, TCP
from threading import Thread, Event
import time
import uuid

app = Flask(__name__)
capture_thread = None
stop_event = Event()
captured_packets = []
target_ports = set()
flow_start_time = None

def packet_callback(pkt):
    global target_ports, flow_start_time

    if IP in pkt and TCP in pkt:
        try:
            if pkt[TCP].dport in target_ports:
                if flow_start_time is None:
                    flow_start_time = time.time()

                packet_info = {
                    "id": str(uuid.uuid4()),
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                    "flow_duration": round(time.time() - flow_start_time, 3),
                    "src_ip": pkt[IP].src,
                    "src_port": pkt[TCP].sport,
                    "dst_ip": pkt[IP].dst,
                    "dst_port": pkt[TCP].dport,
                    "length": len(pkt),
                    "flags": str(pkt[TCP].flags)
                }
                captured_packets.append(packet_info)
        except Exception as e:
            print("Error processing packet:", e)

def capture_packets():
    sniff(prn=packet_callback, stop_filter=lambda x: stop_event.is_set())

@app.route('/start-capture', methods=['POST'])
def start_capture():
    global capture_thread, stop_event, captured_packets, target_ports, flow_start_time

    data = request.get_json()
    if not data or 'ports' not in data:
        return jsonify({"error": "Missing 'ports' list in request body"}), 400

    try:
        ports = data['ports']
        target_ports = set(int(port) for port in ports)
    except Exception as e:
        return jsonify({"error": "Invalid ports format. Must be a list of integers."}), 400

    stop_event.clear()
    captured_packets = []
    flow_start_time = None
    capture_thread = Thread(target=capture_packets)
    capture_thread.start()
    return jsonify({"status": f"Capture started on ports: {sorted(target_ports)}"}), 200

@app.route('/stop-capture', methods=['POST'])
def stop_capture():
    stop_event.set()
    if capture_thread:
        capture_thread.join()
    return jsonify({"status": "Capture stopped", "packets_captured": len(captured_packets)})

@app.route('/packets', methods=['GET'])
def get_all_packets():
    return jsonify(captured_packets)

@app.route('/packet/<string:packet_id>', methods=['GET'])
def get_single_packet(packet_id):
    packet = next((pkt for pkt in captured_packets if pkt["id"] == packet_id), None)
    if packet:
        return jsonify(packet)
    else:
        return jsonify({"error": "Packet not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)

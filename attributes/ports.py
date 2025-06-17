from nfstream import NFStreamer
import pandas as pd

# Load your pcap file
pcap_file = "capture1.pcap"

# Initialize NFStreamer
streamer = NFStreamer(source=pcap_file, statistical_analysis=True)

# Extract flows properly
flows = [flow.get_features() for flow in streamer]

# Create DataFrame from flows
df = pd.DataFrame(flows)

# Show columns for debugging
print("✅ Columns in flow DataFrame:")
print(df.columns.tolist())

# Define features you want
selected_features = [
    'destination_port',
    'flow_duration',
    'total_forward_packets',
    'total_backward_packets',
    'total_length_forward_packets',
    'total_length_backward_packets',
    'fwd_packet_length_max',
    'fwd_packet_length_min',
    'fwd_packet_length_mean',
    'fwd_packet_length_std',
    'bwd_packet_length_max',
    'bwd_packet_length_min',
    'bwd_packet_length_mean',
    'bwd_packet_length_std',
    'flow_bytes_per_second',
    'flow_packets_per_second'
]

# Only keep available features
available = [f for f in selected_features if f in df.columns]
df_selected = df[available]

# Warn if any expected features are missing
missing = set(selected_features) - set(df.columns)
if missing:
    print(f"⚠️ Missing features: {missing}")

# Save selected features to CSV
df_selected.to_csv("filtered_flows.csv", index=False)
print("✅ Saved to filtered_flows.csv")

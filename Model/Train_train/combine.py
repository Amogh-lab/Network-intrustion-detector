import pandas as pd

# List of your CSV filenames
csv_files = [
    "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
    "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
    "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
    "Wednesday-workingHours.pcap_ISCX.csv"
]

# Read and concatenate all CSV files
df_list = [pd.read_csv(file) for file in csv_files]
combined_df = pd.concat(df_list, ignore_index=True)

# Save the combined dataframe to a new CSV
combined_df.to_csv("combined_output.csv", index=False)

print("CSV files combined successfully into combined_output.csv")

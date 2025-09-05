# Network Intrusion Detection Model

This project implements a machine learning model for network intrusion detection using the CICIDS2017 dataset. The model is designed to classify network traffic into multiple categories of cyber attacks and benign activity, helping to identify and mitigate potential security threats in real time.

## Overview

The system utilizes a Random Forest classifier trained on various network traffic features extracted from packet capture data. It processes input network flow data and predicts the type of attack or benign traffic.

## Supported Attack Categories

- BENIGN (Normal traffic)
- DDoS (Distributed Denial of Service)
- DoS GoldenEye
- DoS Hulk
- DoS Slowhttptest
- DoS slowloris
- Heartbleed
- PortScan
- Web Attack – Brute Force
- Web Attack – SQL Injection
- Web Attack – XSS

## Features

- Preprocessing and cleaning of network traffic data
- Encoding of categorical labels for model training
- Handling of infinite and missing values to maintain data integrity
- Prediction based on carefully selected network traffic features
- Easy integration with external systems for real-time traffic classification

## Usage

The model is loaded from a serialized file and accepts network traffic features as input to generate predictions about the nature of the traffic. The output is a label indicating the detected type of network activity.

## Dataset

The training data is derived from the CICIDS2017 dataset, which contains realistic and labeled network traffic, including various attack scenarios and benign behavior.

dataset Link - https://drive.google.com/drive/folders/1fN-AcQUB1D4Hwn9UXK9OiHgNOOxoNn0X?usp=drive_link

## Model

A Random Forest classifier is used for its robustness and effectiveness in handling complex network traffic data with multiple classes.

## Requirements

- Python 3.x
- pandas
- numpy
- scikit-learn
- joblib

## How to Run

1. **Install Requirements**

   Make sure you have Python 3.x installed. Then, install the required packages:

   ```bash
   pip install pandas numpy scikit-learn joblib flask streamlit scapy
   ```

2. **Start the Packet Capture Service**

   Open a terminal and run:
    - This requires root permision for it to work 
    - For Linux system use *sudo* 
    - For Windows Make it *Run as Administrator*
   ```bash
   python3 attributes/capture.py
   ```

   This will start the Flask server for capturing network flows.

3. **Start the Intrusion Detection Dashboard**

   Open another terminal and run:

   ```bash
   streamlit run Detect/server.py
   ```

   This will launch the Streamlit dashboard for real-time intrusion detection.

4. **Usage**

   - The dashboard will automatically start capturing and analyzing network flows.
   - You can manually trigger a capture or enable auto-refresh for continuous monitoring.
   - Prediction results will be displayed in the dashboard.

**Note:** Make sure both services are running simultaneously for

## License

Specify your license here.

## Contact

For questions or feedback, please contact [Amogh A P] at [amoghap099@gmail.com].
" > README.md


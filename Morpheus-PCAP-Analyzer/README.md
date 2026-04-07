# Morpheus PCAP Analyzer (TryHackMe Edition)

## Overview
A GPU-accelerated network packet analysis tool designed for offline CTF (Capture The Flag) competitions and TryHackMe rooms. This pipeline uses NVIDIA Morpheus to ingest `.pcap` files, process them through RAPIDS, and apply machine learning models to highlight anomalies and common attack vectors.

## Objective
Real-time inference on a 10Gbps home network isn't feasible without specialized NICs, but **offline analysis** of PCAP files is perfect for consumer GPUs. This tool replaces the manual bottleneck of digging through Wireshark by automatically flagging suspicious payloads and attack signatures.

## Key Features
- **PCAP to JSON Parser:** A pre-processing step that utilizes `tshark` or Zeek to convert PCAP data into Morpheus-friendly JSON format.
- **RAPIDS Acceleration:** Uses the RTX 5070 Ti's Blackwell architecture for lightning-fast data frame manipulation and preprocessing.
- **Pre-trained ML Models:** Integration of Morpheus's pre-trained network security models (like Digital Fingerprinting).
- **CTF-Specific Fine-tuning:** Custom rules and fine-tuned models to specifically flag common TryHackMe attack vectors (e.g., rapid port scanning, specific exploit payloads, plain-text credential transmission, or Metasploit signatures).

## Architecture
- **Data Source:** `.pcap` files downloaded from CTF platforms.
- **Processing Engine:** NVIDIA Morpheus (Python API).
- **Data Visualization:** Output anomalous traffic to a clean, readable terminal format or a simple web dashboard.
- **Hardware:** NVIDIA RTX 5070 Ti (FP4 acceleration for inference).

## Roadmap / Implementation Steps
1. **Data Ingestion:** Write a script to convert `.pcap` files to JSON logs.
2. **Morpheus Pipeline:** Build a linear pipeline: Source (JSON) -> Preprocessing (RAPIDS cuDF) -> Inference (Triton) -> Action/Output (Terminal).
3. **Model Selection:** Load and configure the appropriate NVIDIA pre-trained model for anomaly detection.
4. **Validation:** Test the pipeline against known TryHackMe `.pcap` files containing brute-force attacks or clear-text FTP logins to verify detection accuracy.

## Use Case
Blue Team CTFs, TryHackMe Network Security rooms, offline incident response training.

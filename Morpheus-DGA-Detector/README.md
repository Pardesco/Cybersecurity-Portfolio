# Morpheus Home Lab DGA Detector

## Overview
A lightweight bridge between a common home DNS sinkhole (like Pi-hole or AdGuard Home) and an NVIDIA Morpheus ML pipeline. This tool detects malware attempting to communicate with Command and Control (C2) servers via Domain Generation Algorithms (DGA).

## Objective
Malware often uses DGAs to hide C2 infrastructure. While enterprise tools rely on complex SIEMs to detect this, this project brings enterprise-grade C2 detection to the home-lab environment. It tails Pi-hole DNS query logs, feeds them into Morpheus running on an RTX 5070 Ti, and flags any device making requests to algorithmically generated domains.

## Key Features
- **Pi-hole Integration:** A custom source stage for Morpheus that tails and parses Pi-hole's `pihole.log` or database in real-time.
- **DGA Inference Model:** Utilizes NVIDIA's pre-trained DGA detection model designed for the Morpheus framework.
- **Low-Overhead Pipeline:** Designed to run continuously in the background on consumer hardware without monopolizing the GPU (leaving room for other tasks).
- **Alerting Mechanism:** Outputs detected DGA requests to a simple Discord webhook or a local text file for home network monitoring.

## Architecture
- **Data Source:** Home DNS Server (Pi-hole / AdGuard).
- **Processing Engine:** NVIDIA Morpheus Pipeline (Real-time stream processing).
- **Hardware:** NVIDIA RTX 5070 Ti (16GB VRAM is ample for this specific model).

## Roadmap / Implementation Steps
1. **Log Parser:** Develop a Python script to continuously tail and format Pi-hole DNS logs into JSON.
2. **Morpheus Integration:** Create a custom Morpheus Source stage that ingests the live JSON stream.
3. **Pipeline Construction:** Build the Morpheus pipeline: Source -> Preprocess -> Inference (DGA Model) -> Filter (Thresholding) -> Output.
4. **Testing:** Simulate DGA traffic on the home network using a Python script (e.g., generating pseudo-random domain lookups) and verify the pipeline triggers an alert.

## Use Case
Home network security monitoring, local SOC (Security Operations Center) dashboards, identifying compromised IoT devices.

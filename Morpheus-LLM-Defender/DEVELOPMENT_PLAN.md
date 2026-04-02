# 🗺️ Morpheus LLM Defender: Development Roadmap to 100%

We have successfully laid the foundational architecture (the 30%). This document outlines the exact step-by-step technical plan to get this project to 100% completion—a fully functional, GPU-accelerated, real-time Prompt Injection detector running on your hardware.

---

## 🟩 Phase 1: Completed (The Architecture - 30%)
* [x] Define Morpheus `pipeline.py` leveraging cuDF and Triton Inference stages.
* [x] Create WSL2/GPU-optimized `docker-compose.yml` for orchestration.
* [x] Generate synthetic `sample_traffic.jsonlines` dataset for testing.
* [x] Write project `README.md` with Mermaid diagrams.

---

## 🟨 Phase 2: The Machine Learning Engine (Target: 50%)
*Morpheus requires a highly optimized model to run on the GPU. We need to fetch a pre-trained transformer and convert it for Triton.*

**Step 2.1: Model Acquisition**
- Download a specialized Hugging Face model (e.g., `ProtectAI/deberta-v3-base-prompt-injection`).
- Download the associated `vocab.txt` or `tokenizer.json` for the Morpheus `PreprocessNLPStage`.

**Step 2.2: ONNX Conversion**
- Write a Python script (`export_model.py`) using `transformers.onnx` or `optimum` to convert the PyTorch model (`.bin`/`.safetensors`) into an optimized `.onnx` format.
- *Why ONNX?* Triton uses the ONNX Runtime (or TensorRT) to maximize your RTX GPU's CUDA cores.

**Step 2.3: Triton Configuration**
- Create the required directory structure: `models/prompt-injection-detector/1/model.onnx`.
- Write the `config.pbtxt` file for Triton. This explicitly defines the input tensors (e.g., `input_ids`, `attention_mask`) and output tensors (e.g., `logits`) so Triton knows how to handle the data from Morpheus.

---

## 🟧 Phase 3: Live Network Ingestion (Target: 75%)
*Replacing the static JSON file with a live packet capture stream from your VirtualBox AD Lab.*

**Step 3.1: Network Sniffer (`sniffer.py`)**
- Write a Python script using `scapy` or `pyshark` (running on the host or a dedicated gateway VM).
- Filter traffic: Only capture packets destined for known LLM endpoints (e.g., `api.openai.com:443`, `api.anthropic.com:443`).

**Step 3.2: SSL/TLS Decryption (The Hard Part)**
- *Challenge:* API traffic is HTTPS (encrypted). 
- *Solution:* Configure your Windows 11 client / AD Lab to use a local Man-in-the-Middle (MitM) proxy (like `mitmproxy` or `Squid`) with a custom Root CA. 
- The proxy intercepts the request, decrypts it, extracts the JSON `prompt` payload, and forwards the data.

**Step 3.3: Kafka / Socket Integration**
- Modify `pipeline.py` to replace `FileSourceStage` with a live stream ingestor (e.g., listening on a UDP socket or a local Kafka topic fed by your MitM proxy).

---

## 🟥 Phase 4: Alerting & Visualization (Target: 95%)
*Turning raw JSON output into actionable SOC alerts.*

**Step 4.1: Splunk Integration**
- Modify `pipeline.py` (or write a sidecar script) to take the output from `WriteToFileStage`.
- Format the alert into a Splunk-compatible JSON schema.
- Send the alert to your local Splunk instance (`localhost:8000`) via the HTTP Event Collector (HEC).

**Step 4.2: Streamlit Dashboard (`dashboard.py`)**
- Build a lightweight Python `streamlit` web app.
- Visualizations: 
  - Live counter of "Total LLM Requests" vs. "Blocked Injections".
  - A data table showing the offending `source_ip` and the exact malicious `prompt`.
  - A real-time gauge of GPU inference latency (proving the value of Morpheus).

---

## 🏁 Phase 5: Open Source Polish (Target: 100%)
*Getting the repository ready for GitHub stars and hiring managers.*

**Step 5.1: Performance Benchmarking**
- Write a `benchmark.py` script that blasts 10,000 synthetic prompts through the pipeline.
- Document the Throughput (Prompts/Second) and Latency (Milliseconds) on your RTX 3060/5070 Ti.

**Step 5.2: Final Documentation**
- Add detailed setup instructions for the MitM proxy and ONNX conversion.
- Add screenshots of the Streamlit dashboard and Splunk alerts.
- Record a 2-minute GIF/video demonstrating a live prompt injection being blocked.

---
*Ready to begin? Start with Phase 2.*
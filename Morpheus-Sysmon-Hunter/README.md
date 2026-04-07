# Morpheus Sysmon NLP Hunter

## Overview
A threat hunting pipeline that ingests Windows Event Logs (EVTX) and uses Natural Language Processing (NLP) models within NVIDIA Morpheus to identify anomalous execution patterns, PowerShell obfuscation, and lateral movement.

## Objective
When playing "blue team" CTF rooms or doing incident response, digging through raw Windows Event Logs is a massive bottleneck. This project leverages the Blackwell architecture of the RTX 5070 Ti to accelerate the text-heavy parsing and analysis of logs, using AI to find "needle in a haystack" attacks.

## Key Features
- **EVTX to JSON Conversion:** A fast preprocessing stage to convert Windows Event logs into a format suitable for Morpheus.
- **GPU-Accelerated NLP:** Uses the RTX 5070 Ti's Tensor Cores to process large volumes of log text using NLP models, rather than relying strictly on regex.
- **Obfuscation Detection:** Specifically trained/configured to identify obfuscated PowerShell commands (e.g., base64 encoding, character substitution) commonly found in Event ID 4104.
- **Anomaly Scoring:** Assigns a risk score to suspicious events, allowing analysts to prioritize their investigation.

## Architecture
- **Data Source:** `.evtx` files from compromised Windows machines (e.g., TryHackMe boxes or local lab).
- **Processing Engine:** NVIDIA Morpheus NLP Pipeline.
- **Hardware:** NVIDIA RTX 5070 Ti (Leveraging FP4/FP8 for efficient NLP inference).
- **Models:** Morpheus pre-trained Sensitive Information Detection (SID) or custom fine-tuned NLP models for command line analysis.
  > *Note:* The current iteration uses the base `microsoft/codebert-base` model. A future enhancement involves fine-tuning this model specifically on a labeled dataset of benign and malicious Sysmon PowerShell commands to optimize its binary classification accuracy.

## Roadmap / Implementation Steps
1. **Data Ingestion:** Integrate a tool like `evtx_dump` to convert EVTX to JSON.
2. **Morpheus Pipeline:** Construct an NLP pipeline: Source -> Tokenization (GPU accelerated) -> Inference -> Post-processing -> Output.
3. **Model Configuration:** Load and test an NLP model capable of parsing command line arguments and identifying anomalous structures.
4. **Validation:** Feed the pipeline logs from a known compromised machine (e.g., a host that executed an Empire or Cobalt Strike payload) and verify the obfuscated commands are flagged.

## Use Case
Incident Response, TryHackMe Blue Team rooms, SOC automation, threat hunting.

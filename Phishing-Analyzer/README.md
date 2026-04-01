# Phishing Analysis Toolkit

This directory contains a Python CLI tool that automates the triage and analysis of suspicious emails to identify potential phishing indicators.

## What It Does
1. Parses raw email headers (`.eml` file input) to extract sending IP, Reply-To vs. From mismatch, and SPF/DKIM/DMARC results.
2. Extracts all URLs from the email body.
3. Checks each URL against the **VirusTotal free tier API**.
4. Checks domain age via WHOIS lookup.
5. Outputs a triage report classifying the email as `MALICIOUS`, `SUSPICIOUS`, or `CLEAN` with supporting evidence.

## Setup & Running
1. Copy `.env.example` to `.env`.
2. Add your free VirusTotal API key to `.env`.
3. Run the Python CLI: `python main.py path/to/email.eml`

## Portfolio Value
Demonstrates practical SOC analyst skills: email header analysis, IOC extraction, interaction with threat intelligence platforms (VirusTotal), scripting automation, and alert triage.
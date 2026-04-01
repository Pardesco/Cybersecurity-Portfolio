# Crypto Incident Response MVP Tool

This directory contains a Python script designed to assist in Web3 / Cryptocurrency Incident Response by analyzing Ethereum wallet addresses for suspicious activity.

## What It Does
1. Takes an Ethereum wallet address as input.
2. Calls the **Etherscan API** to retrieve the last 200 transactions.
3. Identifies token approval transactions and flags any approvals granted to unverified contracts.
4. Checks interacting contract addresses against the **MetaMask phishing detection list** on GitHub.
5. Outputs a structured JSON report including a timeline of events, flagged suspicious contracts, total value transferred out, and recommended immediate actions.

## Setup & Running
1. Copy `.env.example` to `.env`.
2. Add your free Etherscan API key to `.env`.
3. Run the Python script: `python main.py <wallet_address>`

## Portfolio Value
Demonstrates the ability to handle emerging threats (Web3 IR), interact with REST APIs, parse complex JSON data, correlate indicators of compromise (IoCs) against threat intelligence feeds, and output structured artifacts for incident response teams.
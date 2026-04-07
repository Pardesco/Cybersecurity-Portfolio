# Morpheus-Lite: WSL2 & Consumer GPU Starter Kit

## Overview
A streamlined deployment template for running NVIDIA's Morpheus cybersecurity framework on consumer hardware (specifically targeting the RTX 5070 Ti / 16GB VRAM) via WSL2. This project lowers the barrier to entry for home lab enthusiasts and CTF players who want to leverage enterprise AI frameworks without data center infrastructure.

## Objective
The official Morpheus documentation heavily assumes the user has massive enterprise servers (A100s/H100s with 80GB+) and high-speed ConnectX NICs. This repository provides Docker Compose files, memory-optimized configuration templates, and setup scripts designed to run Morpheus pipelines on 16GB GPUs within WSL2.

## Key Features
- **WSL2 Compatibility Layer:** Scripts to handle path translations between Linux (`/mnt/c/...`) and Windows (`C:\...`) seamlessly.
- **Memory-Optimized Profiles:** Pre-configured Triton Inference Server settings designed specifically to fit within a 16GB VRAM limit without Out-Of-Memory (OOM) errors.
- **Docker Compose Deployment:** A single-click deployment stack containing Morpheus, Triton Inference Server, and necessary RAPIDS components.
- **Hardware Validation Script:** An initial script to verify Blackwell architecture support, CUDA 12.8+, and FP4 Tensor Core availability.

## Architecture
- **Host System:** Windows 11 with WSL2 (Ubuntu 22.04/24.04).
- **Hardware:** Minimum 64GB System RAM, NVIDIA RTX 5070 Ti (16GB VRAM).
- **Software Stack:** Docker, NVIDIA Container Toolkit, NVIDIA Morpheus (NGC Container), Triton Inference Server.

## Roadmap / Implementation Steps
1. **Environment Setup Script:** Create a `.bat`/`.sh` combo to install WSL2 dependencies and the NVIDIA Container Toolkit.
2. **Docker Compose Composition:** Draft the `docker-compose.yml` to pull the correct Morpheus and Triton images.
3. **Pipeline Template:** Write a basic "Hello World" Morpheus pipeline in Python that passes a small text file through a pre-trained model to ensure the pipeline is functioning.
4. **Documentation:** Write a comprehensive guide on common WSL2 networking and VRAM troubleshooting steps for Morpheus.

## Use Case
Foundation for all other consumer-grade Morpheus projects in the home lab.

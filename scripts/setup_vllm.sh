#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Creating vLLM isolated environment..."
python3 -m venv .venv-vllm
source .venv-vllm/bin/activate

echo "Upgrading packaging tools..."
python -m pip install --upgrade pip setuptools wheel

echo "Installing vLLM >= 0.9.0..."
pip install "vllm>=0.9.0"

echo "Verifying vLLM installation..."
python -c "import vllm; print('vLLM Version:', vllm.__version__)"

echo "Verifying CUDA environment..."
nvidia-smi

echo "vLLM environment setup complete. Remember to activate using: source .venv-vllm/bin/activate"

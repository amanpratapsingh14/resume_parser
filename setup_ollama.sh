#!/bin/bash
# Install Ollama (if not already installed)
if ! command -v ollama &> /dev/null; then
  echo "Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "Ollama is already installed."
fi

# Start Ollama service (if not already running)
if ! pgrep -x "ollama" > /dev/null; then
  echo "Starting Ollama service..."
  ollama serve &
  sleep 2
else
  echo "Ollama service is already running."
fi

# Download the required model
if ! ollama list | grep -q "qwen3:0.6b"; then
  echo "Downloading qwen3:0.6b model..."
  ollama run qwen3:0.6b
else
  echo "qwen3:0.6b model is already downloaded."
fi 
#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Confirming model server..."
curl http://127.0.0.1:8100/v1/models

echo -e "\n\nRunning basic direct Qwen test..."
curl http://127.0.0.1:8100/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-8B-AWQ",
    "messages": [
      {
        "role": "system",
        "content": "Reply in one short sentence suitable for a phone call."
      },
      {
        "role": "user",
        "content": "Say hello and ask for my name."
      }
    ],
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 20,
    "max_tokens": 40,
    "chat_template_kwargs": {
      "enable_thinking": false
    }
  }'
echo -e "\n\nTest complete."

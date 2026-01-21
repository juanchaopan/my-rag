#!/bin/bash
curl http://ollama:11434/api/generate \
-H "Content-Type: application/json" \
-d '{
    "model": "deepseek-r1:8b",
    "prompt": "",
    "stream": false
}'


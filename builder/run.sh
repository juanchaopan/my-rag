#!/bin/bash
curl -X POST http://ollama:11434/api/generate \
-H "Content-Type: application/json" \
-d '{
    "model": "deepseek-r1:8b",
    "prompt": "",
    "stream": false
}'
curl -X POST http://ollama:11434/api/embed \
-H "Content-Type: application/json" \
-d '{
    "model": "nomic-embed-text",
    "prompt": "",
    "stream": false
}'


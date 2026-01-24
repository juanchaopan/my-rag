#!/bin/bash
curl -X POST http://ollama:11434/api/pull \
-d '{
    "model": "deepseek-r1:8b"
}'
curl -X POST http://ollama:11434/api/pull \
-d '{
    "model": "nomic-embed-text"
}'
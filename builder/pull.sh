#!/bin/bash
curl http://ollama:11434/api/pull \
-d '{
    "model": "deepseek-r1:8b"
}'

@echo off
start "" code .
start "" code ./builder
start "" code ./query
start "" code ./langchain-ai-docs
docker compose up -d chroma
docker compose up -d ollama
exit

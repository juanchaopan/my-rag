@echo off
start "" code .
start "" code ./builder
start "" code ./langchain-ai-docs
docker compose up -d ollama

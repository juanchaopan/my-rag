#!/bin/bash
mkdir -p logs
scrapy crawl docs_spider -o langchain-ai-docs.jsonl -s LOG_LEVEL=ERROR -s LOG_FILE=logs/scrapy.log

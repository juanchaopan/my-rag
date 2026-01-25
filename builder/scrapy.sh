#!/bin/bash
scrapy crawl docs_spider -o langchain-ai-docs.jsonl -s LOG_LEVEL=ERROR

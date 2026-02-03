#!/bin/bash
curl -X POST "http://localhost:8000/chat" \
-H "Content-Type: application/json" \
-d '[
  {"role":"user","content":"How to use streaming in Langchain? Provide code examples and explanations in Chinese."}
]'
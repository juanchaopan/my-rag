rm -rf /app/docs
git clone --depth 1 https://github.com/langchain-ai/docs.git /app/docs
cd /app/docs
make install
make build

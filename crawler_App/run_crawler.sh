#!/bin/bash

cd "$(dirname "$0")"

echo "🚀 Starting Reddit Crawler"
echo "Timestamp: $(date)"

mkdir -p logs

# Cross-platform: force real-time logging
python3 -u crawler.py | tee "logs/crawler_$(date +%Y-%m-%d_%H-%M-%S).log"

echo "✅ Crawler finished at $(date)"

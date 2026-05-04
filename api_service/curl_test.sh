#!/bin/bash

# Configuration
API_URL="http://127.0.0.1:8000"
API_KEY=${ANALYTICS_API_KEY:-"default_secret_key"}

echo "------------------------------------------------"
echo "Phase 4: FastAPI Service Testing"
echo "------------------------------------------------"

# 1. Test Health Endpoint
echo -e "\n[1/4] Testing Health Endpoint..."
curl -s "$API_URL/health" | python -m json.tool

# 2. Test Sentiment Endpoint (Unauthorized - No Key)
echo -e "\n[2/4] Testing Sentiment Endpoint (Unauthorized - No Key)..."
curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/v1/sentiment/1"
echo -e " (Expected: 401)"

# 3. Test Sentiment Endpoint (Authorized)
echo -e "\n[3/4] Testing Sentiment Endpoint (Authorized)..."
curl -s -H "X-API-Key: $API_KEY" "$API_URL/api/v1/sentiment/1" | python -m json.tool

# 4. Test Sentiment Endpoint (Invalid Product ID)
echo -e "\n[4/4] Testing Sentiment Endpoint (Invalid Product ID)..."
curl -s -H "X-API-Key: $API_KEY" "$API_URL/api/v1/sentiment/999" | python -m json.tool
echo -e " (Expected: 404)"

echo -e "\n------------------------------------------------"
echo "Testing Complete"
echo "------------------------------------------------"

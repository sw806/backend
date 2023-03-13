#!/bin/sh

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

docker compose up -d
sleep 1s
curl --fail --retry 10 http://0.0.0.0:8010/api/v1/status \
    && echo "" && echo "${GREEN}==============================Sanity check PASSED!==============================${NC}" && exit 0\
    || echo "${RED}==============================Sanity check FAILED!==============================${NC}" && exit -1
echo ""
docker compose down
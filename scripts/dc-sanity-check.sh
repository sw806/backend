#!/bin/sh

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
EXIT=0

docker compose up -d
sleep 1s
curl --fail --retry 10 http://0.0.0.0:8000/api/v1/status \
    && echo "" && echo "${GREEN}==============================Sanity check PASSED!==============================${NC}" \
    || echo "${RED}==============================Sanity check FAILED!==============================${NC}" && EXIT=1
echo ""
docker compose down
exit ${EXIT}
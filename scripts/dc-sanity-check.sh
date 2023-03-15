#!/bin/sh

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
EXIT=0

docker compose up --quiet-pull --wait --detach
sleep 1s
if curl --fail --retry 10 http://0.0.0.0:8000/api/v1/status; then
    echo ""
    echo "${GREEN}==============================Sanity check PASSED!==============================${NC}"
else
    echo ""
    echo "${RED}==============================Sanity check FAILED!==============================${NC}"
    EXIT=1
fi;
docker compose down
exit ${EXIT}
#!/usr/bin/env bash
SIG=${1:-TERM}
ps -ef | grep "start_grpc_service" | grep -v "grep" | awk '{print $2}' | xargs kill -$SIG

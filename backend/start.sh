#!/bin/sh
set -e

PORT_VALUE="${PORT:-8173}"
ARGS="app.main:app --host 0.0.0.0 --port ${PORT_VALUE}"

if [ "${BEHIND_PROXY:-false}" = "true" ]; then
    FORWARDED_IPS="${FORWARDED_ALLOW_IPS:-*}"
    ARGS="$ARGS --proxy-headers --forwarded-allow-ips=$FORWARDED_IPS"
fi

# shellcheck disable=SC2086
exec uvicorn $ARGS

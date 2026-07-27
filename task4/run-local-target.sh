#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NETWORK_NAME="task4-ssrf-lab"

docker build -t ledger-api:vuln "${ROOT_DIR}/local-target"
docker rm -f ledger-api-vuln >/dev/null 2>&1 || true
docker rm -f ssrf-target >/dev/null 2>&1 || true
docker network inspect "${NETWORK_NAME}" >/dev/null 2>&1 || docker network create "${NETWORK_NAME}" >/dev/null

# The unexposed target gives the SSRF exercise a deterministic internal-only service.
docker run -d --name ssrf-target --network "${NETWORK_NAME}" --network-alias internal-target ledger-api:vuln >/dev/null
docker run -d --name ledger-api-vuln --network "${NETWORK_NAME}" -p 18080:8080 ledger-api:vuln >/dev/null

for attempt in {1..15}; do
  if curl --fail --silent http://127.0.0.1:18080/health >/dev/null; then
    break
  fi
  sleep 1
done

if ! curl --fail --silent http://127.0.0.1:18080/health >/dev/null; then
  echo "Vulnerable target did not become ready within 15 seconds." >&2
  exit 1
fi

echo "Vulnerable target: http://127.0.0.1:18080"
echo "Internal-only SSRF target: http://internal-target:8080 (reachable only from the lab network)"

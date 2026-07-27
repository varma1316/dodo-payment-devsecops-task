#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_SECRET="$(mktemp)"

cleanup() {
  rm -f "${TMP_SECRET}"
}

trap cleanup EXIT

if [[ -z "${SOPS_AGE_KEY_FILE:-}" ]]; then
  export SOPS_AGE_KEY_FILE="${ROOT_DIR}/.age-key.txt"
fi

if [[ ! -f "${SOPS_AGE_KEY_FILE}" ]]; then
  echo "Missing age key file: ${SOPS_AGE_KEY_FILE}" >&2
  exit 1
fi

pushd "${ROOT_DIR}" >/dev/null

docker build -t ledger-api:secure ./app
kind load docker-image ledger-api:secure --name security-lab
sops --decrypt k8s/base/secret.enc.yaml > "${TMP_SECRET}"

kubectl apply -f policies/kyverno
kubectl apply -f gitops/bootstrap
kubectl apply -f k8s/base/namespace.yaml
kubectl label namespace payments pod-security.kubernetes.io/enforce- --overwrite || true
kubectl apply -f "${TMP_SECRET}"
kubectl apply -k k8s/overlays/local
kubectl apply -k istio

kubectl -n payments rollout status deploy/ledger-api --timeout=180s
kubectl -n payments rollout status deploy/reporting --timeout=180s
kubectl -n payments rollout status deploy/intruder --timeout=180s

popd >/dev/null

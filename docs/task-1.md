# Task 1 - Deploy and Harden the Workload

## What Changed

- Preserved the original insecure manifests in [`deploy/`](/Users/harshith/dodo-security-assessment/ledger-api-assignment/deploy) for negative testing
- Rebuilt the container on `python:3.12-slim` with a non-root runtime user
- Replaced plaintext Kubernetes env vars with an encrypted SOPS secret in [`k8s/base/secret.enc.yaml`](/Users/harshith/dodo-security-assessment/ledger-api-assignment/k8s/base/secret.enc.yaml)
- Added dedicated service accounts, least-privilege RBAC, resource requests and limits, and probes
- Enforced namespace Pod Security Admission labels and Kyverno guardrails
- Added a neighbour workload (`reporting`) plus an unauthorized client (`intruder`) for access-control proofing

## Security Decisions

- `automountServiceAccountToken: false` is set everywhere because the app does not need in-cluster API access by default.
- The only RBAC granted to `ledger-api` is read access to its own ConfigMap.
- `readOnlyRootFilesystem` is paired with a small `/tmp` `emptyDir` so the app remains functional without a writable rootfs.
- The starter app exposed raw PAN values and used unsafe YAML parsing. Those were fixed in [`app/app.py`](/Users/harshith/dodo-security-assessment/ledger-api-assignment/app/app.py).
- This repo keeps Pod Security Admission at `restricted` audit and warn on this cluster instead of enforcement. Mesh-injected pods are blocked by PSA enforcement because Istio CNI is not installed and `istio-init` needs extra network capabilities. The production follow-up is to enable Istio CNI and then raise `enforce` to `restricted`.

## Admission Controls

Kyverno policies enforce:

- non-root runtime plus `RuntimeDefault` seccomp
- no `:latest` tags
- signed `ledger-api` images only

Apply the original [`deploy/deployment.yaml`](/Users/harshith/dodo-security-assessment/ledger-api-assignment/deploy/deployment.yaml) with a temporary deployment name after the policies are installed to demonstrate rejection without colliding with the running workload:

```bash
sed 's/^  name: ledger-api$/  name: ledger-api-insecure-demo/' deploy/deployment.yaml | kubectl apply -f -
```

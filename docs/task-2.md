# Task 2 - Secure CI/CD Pipeline and Supply Chain

## Pipeline Stages

The GitHub Actions workflow in [`.github/workflows/ci-cd.yaml`](/Users/harshith/dodo-security-assessment/ledger-api-assignment/.github/workflows/ci-cd.yaml) enforces:

1. `Semgrep` SAST on the application source
2. `Gitleaks` secret scanning on the repository
3. `Trivy` filesystem scan for dependency and misconfiguration issues
4. container build and push to `ghcr.io`
5. `Trivy` image scan on the built artifact
6. `Cosign` keyless signing
7. `Cosign attest` for a lightweight SLSA-style provenance statement
8. GitOps promotion by updating the production Kustomize overlay

## Gate Policy

- Hard fail:
  `Semgrep`, `Gitleaks`, Trivy `HIGH` and `CRITICAL` findings, image build failure, signing failure
- Soft warning:
  medium or lower CVEs tracked in backlog with due dates
- No-fix CVE handling:
  pin the least-bad version, document compensating controls, add a risk acceptance entry, and keep the gate failing only for exploitable `HIGH` or `CRITICAL` issues

## GitOps

ArgoCD watches [`k8s/overlays/prod`](/Users/harshith/dodo-security-assessment/ledger-api-assignment/k8s/overlays/prod). The CI pipeline updates the image tag in Git, not in the cluster directly, so Git remains the source of truth and ArgoCD handles sync, drift detection, pruning, and self-heal.

The production overlay keeps the secret encrypted in Git. In a real deployment, ArgoCD should be configured with a SOPS decryption plugin such as KSOPS or a repo-server sidecar so the secret can be rendered server-side without exposing plaintext in the repository.

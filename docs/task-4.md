# Task 4 - Reconnaissance and Penetration Testing

## Scope

For Part A, I kept the work passive: public search results, official documentation, public GitHub repositories, and the public status page. I did not scan, fuzz, authenticate to, or attempt to exploit any Dodo-owned system. The observations below were collected on July 27, 2026.

For Part B, I tested the bundled vulnerable starter application locally. This was the authorised target supplied with the exercise and makes every finding reproducible from this repository.

## Part A - Passive Attack Surface Summary

Observed public-facing properties from public sources:

- `status.dodopayments.com`
- `docs.dodopayments.com`
- `customer.dodopayments.com`
- `test.customer.dodopayments.com`
- `live.dodopayments.com`
- `test.dodopayments.com`

Key observations:

- The public status page enumerates meaningful internal service categories such as dashboard, docs, checkout, customer portal, webhook services, and prod/test APIs.
- Official documentation openly documents separate test and live API hostnames, which is normal for developer products but useful to an attacker mapping environment boundaries.
- The unified customer portal is internet-facing and email-based, making it a high-value surface for phishing, account-takeover attempts, and credential-stuffing defenses.

## Part B - Local Test Summary

The local target reflects the insecure starter implementation before the hardening work. I confirmed the following issues:

1. Unauthenticated PAN disclosure via `GET /transactions`
2. SSRF via `GET /fetch?url=...`
3. Unsafe YAML deserialization risk via `POST /import`

The full report is in [`task-4-report.md`](task-4-report.md).

## Run the Local Lab

```bash
./task4/run-local-target.sh
```

The script starts the vulnerable API at `http://127.0.0.1:18080` and an unexposed `internal-target` container on the same private Docker network. The latter is used only to reproduce the SSRF finding without contacting an external system.

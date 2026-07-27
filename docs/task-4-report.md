# Task 4 Report

Assessment date: July 27, 2026

## Executive Summary

The passive review shows a public footprint around the API, documentation, status page, and customer portal. Nothing in this phase involved active testing of a Dodo-owned host. The useful takeaway is that the public material clearly distinguishes live and test environments and identifies customer-facing flows. That is expected for a developer platform, but it gives an attacker a useful starting point for phishing and authentication-focused attacks.

The authorized local pentest of the bundled vulnerable starter app identified two confirmed high-severity issues and one medium-severity issue:

- High: unauthenticated exposure of full payment-card PANs
- High: SSRF through a server-side fetch endpoint
- Medium: unsafe YAML deserialization risk

## Methodology

- Part A: passive-only review of public search results, official Dodo documentation, the public status page, and public GitHub repositories
- Part B: local black-box testing of the intentionally vulnerable starter service using HTTP requests only

## Part A - Passive Recon

### Publicly observed hosts

The following hosts were observed from public sources on July 27, 2026:

- `status.dodopayments.com`
- `docs.dodopayments.com`
- `customer.dodopayments.com`
- `test.customer.dodopayments.com`
- `live.dodopayments.com`
- `test.dodopayments.com`

### Technology and exposure notes

- `status.dodopayments.com`
  Public status site exposing service group names including Website, Dashboard, Docs, Checkout, Customer Portal, Live Mode Prod APIs, Test Mode Prod APIs, Internal Prod APIs, Email Services, and Webhook Services.
- `docs.dodopayments.com`
  Public developer documentation disclosing API hostnames, customer portal entrypoints, and integration workflows.
- `customer.dodopayments.com`
  Public customer portal with email-based access flow.
- `test.customer.dodopayments.com`
  Public test customer portal flow documented for test-mode business IDs.
- `live.dodopayments.com`
  Documented live API host.
- `test.dodopayments.com`
  Documented test API host.

### Risk observations

- The public status page materially improves attacker reconnaissance by enumerating business-critical surfaces and environment splits.
- The customer portal is a natural target for phishing and account enumeration controls because the UX is email-driven.
- Test and live separation is documented clearly, which is good for developers but gives attackers a straightforward path to target lower-friction test-mode assets first.

## Part B - Authorized Local Pentest

### Target

- Local target: bundled vulnerable starter app in [`task4/local-target/`](/Users/harshith/dodo-security-assessment/ledger-api-assignment/task4/local-target)
- Access: black-box HTTP only, no source modification during testing

### Finding 1 - Unauthenticated PAN disclosure

- Severity: High
- CVSS v3.1: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`
- Score: 7.5
- Endpoint: `GET /transactions`

Description:
The endpoint returns transaction objects containing full PAN values with no authentication or masking.

Reproduction:

```bash
curl http://127.0.0.1:18080/transactions
```

Observed result:
The response returned full PAN values such as `4242424242424242` and `5555555555554444`.

Impact:
Any network-reachable user can retrieve cardholder data directly, creating immediate PCI DSS and breach-notification exposure.

Remediation:
- Require authentication and authorization on all transaction endpoints
- Never return full PANs
- Store and expose only tokens plus masked card data

### Finding 2 - SSRF via server-side fetch endpoint

- Severity: High
- CVSS v3.1: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L`
- Score: 8.1
- Endpoint: `GET /fetch?url=...`

Description:
The endpoint performs arbitrary server-side HTTP requests to a caller-supplied URL and returns response content.

Reproduction:

```bash
./task4/run-local-target.sh
curl "http://127.0.0.1:18080/fetch?url=http://internal-target:8080/transactions"
```

Observed result:
The vulnerable service fetched the private `internal-target` container's `/transactions` endpoint and returned a `200` response body through `/fetch`, including the full PAN values.

Impact:
An attacker can pivot into internal-only HTTP services, cloud metadata services, localhost admin ports, or mesh-only backends if network paths exist.

Remediation:
- Remove the feature if not strictly required
- If needed, require authentication, strict allowlisting, HTTPS-only, and DNS/IP validation against internal ranges

### Finding 3 - Unsafe YAML deserialization risk

- Severity: Medium
- CVSS v3.1: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L`
- Score: 6.5
- Endpoint: `POST /import`

Description:
The endpoint accepts arbitrary YAML and parses it unsafely in the original starter application.

Reproduction:

```bash
curl -X POST http://127.0.0.1:18080/import \
  -H 'Content-Type: application/x-yaml' \
  --data-binary $'a: 1\nb: 2'
```

Observed result:
The service accepts and parses arbitrary YAML input. In the original code path, this used unsafe loading semantics.

Impact:
Depending on loader behavior and dependency version, unsafe YAML parsing can enable deserialization abuse, denial of service, or future code-execution paths when dangerous object types are accepted.

Remediation:
- Use `yaml.safe_load`
- Validate input schema before processing
- Prefer JSON for untrusted client input

## Retest Mapping

The hardened app in [`app/app.py`](/Users/harshith/dodo-security-assessment/ledger-api-assignment/app/app.py) addresses these findings by:

- removing PAN exposure from transaction responses
- validating and restricting the fetch target
- switching to `yaml.safe_load`

## Sources

- [Dodo Payments status](https://status.dodopayments.com/)
- [API Introduction](https://docs.dodopayments.com/api-reference/introduction)
- [Test Mode vs Live Mode](https://docs.dodopayments.com/miscellaneous/test-mode-vs-live-mode)
- [Customer Portal docs](https://docs.dodopayments.com/features/customer-portal)
- [Dodo docs GitHub repository](https://github.com/dodopayments/dodo-docs)

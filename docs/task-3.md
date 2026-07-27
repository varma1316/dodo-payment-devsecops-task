# Task 3 - Service Mesh and Zero-Trust

## Mesh Controls

- [`istio/peer-authentication.yaml`](/Users/harshith/dodo-security-assessment/ledger-api-assignment/istio/peer-authentication.yaml) sets namespace-wide `STRICT` mTLS.
- [`istio/authorization-policy.yaml`](/Users/harshith/dodo-security-assessment/ledger-api-assignment/istio/authorization-policy.yaml) creates a default deny for `ledger-api` and then allows only the `reporting` service account principal.
- [`istio/destination-rule.yaml`](/Users/harshith/dodo-security-assessment/ledger-api-assignment/istio/destination-rule.yaml) enforces `ISTIO_MUTUAL`.
- [`istio/gateway.yaml`](/Users/harshith/dodo-security-assessment/ledger-api-assignment/istio/gateway.yaml) and [`istio/virtual-service.yaml`](/Users/harshith/dodo-security-assessment/ledger-api-assignment/istio/virtual-service.yaml) expose the service through the Istio ingress gateway.

## Identity Model

Istio issues an X.509 workload certificate to each sidecar from the mesh CA rooted in `istiod`. The SPIFFE identity format used by the authorization policy is:

`spiffe://cluster.local/ns/payments/sa/<service-account>`

Istio rotates these workload certificates automatically before expiration. The trust root is the mesh CA configured in `istiod`, which is then distributed to workloads through Envoy bootstrap and SDS.

## Defense in Depth

- Istio `PeerAuthentication` and `AuthorizationPolicy` protect L7 and workload identity, including request methods and paths.
- Kubernetes `NetworkPolicy` blocks unwanted east-west traffic even if a pod lacks a sidecar, the mesh policy is misconfigured, or an attacker tries direct IP connectivity at L3/L4.
- On this local Istio version, `istioctl authn tls-check` is not available. The equivalent proof used here is `istioctl x describe pod <reporting-pod> -n payments`, which showed `Effective PeerAuthentication: Workload mTLS mode: STRICT`.

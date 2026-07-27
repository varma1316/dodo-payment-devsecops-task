# Evidence Index

The screenshots below were captured from the local kind cluster and the authorised Task 4 vulnerable lab. No production Dodo Payments system was actively tested.

| Evidence | What it demonstrates |
| --- | --- |
| [01 - Deployed workloads](screenshots/01-deployed-workloads.png) | Running `ledger-api`, `reporting`, and `intruder` workloads, including Istio sidecars and dedicated service accounts. |
| [02 - Workload hardening](screenshots/02-workload-hardening.png) | `RuntimeDefault` seccomp, non-root execution, dropped Linux capabilities, read-only root filesystem, and ready Kyverno policies. |
| [03 - Kyverno rejection](screenshots/03-kyverno-rejection.png) | The original insecure Deployment is rejected by Pod Security checks and the Kyverno non-root policy. |
| [04 - Network and mesh policies](screenshots/04-network-and-mesh-policies.png) | Default-deny NetworkPolicy, explicit reporting access, strict PeerAuthentication, and Istio authorization policies. |
| [05 - Strict mTLS](screenshots/05-strict-mtls.png) | `istioctl` reports effective workload mTLS mode as `STRICT`. |
| [06 - Identity-based access](screenshots/06-identity-based-access.png) | `reporting` receives `200`; the unauthorised `intruder` request times out with `000`. |
| [07 - PAN disclosure PoC](screenshots/07-task4-pan-disclosure.png) | The local vulnerable lab returns full synthetic test PANs without authentication. |
| [08 - SSRF PoC](screenshots/08-task4-ssrf.png) | The local vulnerable app retrieves an internal-only service through the caller-controlled fetch endpoint. |

The Task 4 PoC screenshots use synthetic card numbers in an isolated local Docker network. They are included only to document the authorised assessment finding and do not contain production cardholder data.

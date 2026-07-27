# Verification

## Render Manifests

```bash
kubectl kustomize k8s/overlays/prod
kubectl kustomize istio
```

## Deploy and Check Pods

```bash
./scripts/deploy-local.sh
kubectl -n payments get pods
kubectl -n payments get peerauthentication,authorizationpolicy
```

## Demonstrate Policy Rejection

```bash
sed 's/^  name: ledger-api$/  name: ledger-api-insecure-demo/' deploy/deployment.yaml | kubectl apply -f -
```

The temporary name avoids colliding with the running hardened Deployment, whose selector is immutable. Expected result: admission denial for root execution and the missing hardened security context. The rejected resource is never created.

## Prove mTLS and Identity-Based Authorization

```bash
istioctl x describe pod "$(kubectl -n payments get pod -l app.kubernetes.io/name=reporting -o jsonpath='{.items[0].metadata.name}')" -n payments
kubectl -n payments exec deploy/reporting -c reporting -- curl -sS -o /dev/null -w '%{http_code}\n' http://ledger-api:8080/health
kubectl -n payments exec deploy/intruder -c intruder -- curl --max-time 5 -sS -o /dev/null -w '%{http_code}\n' http://ledger-api:8080/health
```

Expected result: `reporting` returns `200` and `intruder` times out with `000`, showing the request never reaches the app.

## Prove ArgoCD Self-Heal

```bash
kubectl -n payments patch deploy ledger-api --type merge -p '{"spec":{"replicas":1}}'
kubectl -n argocd get application ledger-api
kubectl -n payments get deploy ledger-api
```

Expected result: ArgoCD marks the app `OutOfSync`, then restores the declared replica count of `3`.

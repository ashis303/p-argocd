# p-argocd

ArgoCD GitOps repository — Kubernetes application manifests managed and synced via ArgoCD.

---

## Repository Structure

```
p-argocd/
├── argocd/
│   └── applications/          # ArgoCD Application CRD manifests
│       ├── sample-app.yaml        # Dev environment Application
│       └── sample-app-prod.yaml   # Prod environment Application
└── apps/
    └── sample-app/            # Kubernetes manifests (Kustomize)
        ├── base/              # Shared base manifests
        │   ├── namespace.yaml
        │   ├── deployment.yaml
        │   ├── service.yaml
        │   └── kustomization.yaml
        └── overlays/
            ├── dev/           # Dev-specific patches (1 replica)
            │   ├── deployment-patch.yaml
            │   └── kustomization.yaml
            └── prod/          # Prod-specific patches (3 replicas)
                ├── deployment-patch.yaml
                └── kustomization.yaml
```

---

## Getting Started

### 1. Install ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### 2. Register ArgoCD Applications

Apply the ArgoCD Application manifests from this repo to let ArgoCD track and sync your apps:

```bash
# Dev environment
kubectl apply -f argocd/applications/sample-app.yaml

# Prod environment
kubectl apply -f argocd/applications/sample-app-prod.yaml
```

ArgoCD will automatically pull the Kubernetes manifests from the `apps/` directory in this repository and apply them to your cluster.

### 3. Adding Your Own Application

1. Create a new directory under `apps/<your-app>/`:
   - `base/` — shared Kubernetes manifests (Deployment, Service, etc.)
   - `overlays/dev/` and `overlays/prod/` — environment-specific patches

2. Add a corresponding ArgoCD `Application` manifest under `argocd/applications/<your-app>.yaml`, pointing `spec.source.path` to the correct overlay.

3. Apply the Application manifest with `kubectl apply`.

---

## Sync Policy

All ArgoCD Applications in this repo are configured with **automated sync**:
- `prune: true` — removes resources deleted from Git
- `selfHeal: true` — reverts any manual changes in the cluster back to the Git state

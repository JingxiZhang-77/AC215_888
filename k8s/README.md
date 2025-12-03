# Kubernetes Deployment Guide

This guide covers deploying the Safety Event Classification System to a Kubernetes cluster on Google Kubernetes Engine (GKE) with auto-scaling capabilities.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  Kubernetes Cluster                      │
│                                                          │
│  ┌────────────┐     ┌──────────────┐    ┌───────────┐ │
│  │  Frontend  │────▶│   API (HPA)  │───▶│ ChromaDB  │ │
│  │   (2-6)    │     │    (3-10)    │    │    (1)    │ │
│  │   pods     │     │    pods      │    │  StatefulSet│
│  └────────────┘     └──────────────┘    └───────────┘ │
│        │                    │                   │       │
│   LoadBalancer         LoadBalancer        ClusterIP   │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

### Required Tools
- `kubectl` (Kubernetes CLI)
- `gcloud` (Google Cloud SDK)
- Docker
- Apache Bench (`ab`) for load testing

### GCP Setup
- GCP Project: `apcomp215-group88`
- Region: `us-central1`
- Service account credentials: `secrets/llm-service-account.json`

## Quick Start

### 1. Deploy to Kubernetes

```bash
# Make scripts executable
chmod +x k8s/deploy.sh k8s/load-test.sh

# Run deployment script
./k8s/deploy.sh
```

The deployment script will:
1. Create/verify GKE cluster
2. Build and push Docker images to GCR
3. Create Kubernetes namespace
4. Deploy ChromaDB (StatefulSet)
5. Deploy API (Deployment with HPA)
6. Deploy Frontend (Deployment with HPA)
7. Configure auto-scaling policies

### 2. Verify Deployment

```bash
# Check all resources
kubectl get all -n safety-event-system

# Check HPA status
kubectl get hpa -n safety-event-system

# Get external IPs
kubectl get services -n safety-event-system
```

### 3. Access the Application

```bash
# Get Frontend URL
FRONTEND_IP=$(kubectl get service frontend-service -n safety-event-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Frontend: http://${FRONTEND_IP}"

# Get API URL
API_IP=$(kubectl get service api-service -n safety-event-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "API: http://${API_IP}:9000/api/docs"
```

## Auto-Scaling Configuration

### API Horizontal Pod Autoscaler (HPA)

```yaml
minReplicas: 3
maxReplicas: 10
CPU threshold: 70%
Memory threshold: 80%
```

**Scaling Behavior:**
- **Scale Up**: Fast response (30-60s stabilization)
  - Add up to 100% more pods or 2 pods (whichever is greater)
- **Scale Down**: Conservative (5 min stabilization)
  - Remove up to 50% of pods per minute

### Frontend HPA

```yaml
minReplicas: 2
maxReplicas: 6
CPU threshold: 70%
Memory threshold: 80%
```

## Demonstrating Auto-Scaling

### Method 1: Automated Load Test

Run the provided load test script:

```bash
./k8s/load-test.sh
```

This script will:
1. **Phase 1 (Baseline)**: Show initial state with minimum replicas (3 pods)
2. **Phase 2 (Medium Load)**: Send 10,000 requests with 20 concurrent users
   - Expected: Scale up to 5-6 pods
3. **Phase 3 (High Load)**: Send 50,000 requests with 50 concurrent users
   - Expected: Scale up to 8-10 pods (max capacity)
4. **Phase 4 (Cool Down)**: Stop load and observe scale-down
   - Expected: Gradually return to 3 pods over 5-10 minutes

### Method 2: Manual Load Testing

#### Step 1: Monitor HPA in real-time

```bash
# Watch HPA status
kubectl get hpa -n safety-event-system --watch

# Watch pods in another terminal
kubectl get pods -l app=safety-event-api -n safety-event-system --watch
```

#### Step 2: Generate load

```bash
# Get API URL
API_URL=$(kubectl get service api-service -n safety-event-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Light load (baseline)
ab -n 1000 -c 5 -t 30 http://${API_URL}:9000/api/v1/health

# Medium load (should trigger scale-up)
ab -n 10000 -c 20 -t 60 http://${API_URL}:9000/api/v1/health

# Heavy load (scale to max)
ab -n 50000 -c 50 -t 90 http://${API_URL}:9000/api/v1/health
```

#### Step 3: Observe scaling

```bash
# Check current metrics
kubectl top pods -n safety-event-system

# View HPA decisions
kubectl describe hpa api-hpa -n safety-event-system

# View scaling events
kubectl get events -n safety-event-system --sort-by='.lastTimestamp' | grep -i scale
```

### Method 3: CPU Stress Test

```bash
# Deploy a load generator pod
kubectl run -it --rm load-generator \
  --image=busybox:latest \
  --restart=Never \
  -n safety-event-system \
  -- /bin/sh -c "while true; do wget -q -O- http://api-service:9000/api/v1/health; done"
```

## Expected Scaling Behavior

### Scale-Up Timeline

| Time | Load | CPU Usage | Expected Pods | Action |
|------|------|-----------|---------------|--------|
| 0s   | None | <10%      | 3 (min)       | Baseline |
| 30s  | Low  | 30-40%    | 3             | Stable |
| 60s  | Medium | 70-80%  | 5-6           | Scale up triggered |
| 120s | High | 85-90%    | 8-10          | Scale to max |

### Scale-Down Timeline

| Time After Load Stops | CPU Usage | Expected Pods | Action |
|-----------------------|-----------|---------------|--------|
| 0-5 min              | Decreasing | 8-10         | Stabilization window |
| 5-7 min              | <50%      | 6-7          | Begin scale down |
| 8-10 min             | <30%      | 4-5          | Continue scale down |
| 12-15 min            | <20%      | 3 (min)      | Return to baseline |

## Resource Configuration

### API Pods

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

### Frontend Pods

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### ChromaDB (StatefulSet)

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
storage: 10Gi (persistent)
```

## Monitoring and Debugging

### View Logs

```bash
# API logs
kubectl logs -f deployment/api-deployment -n safety-event-system

# Frontend logs
kubectl logs -f deployment/frontend-deployment -n safety-event-system

# ChromaDB logs
kubectl logs -f statefulset/chromadb -n safety-event-system
```

### Check Resource Usage

```bash
# Current CPU/Memory usage
kubectl top nodes
kubectl top pods -n safety-event-system

# Detailed pod information
kubectl describe pod <pod-name> -n safety-event-system
```

### View HPA Metrics

```bash
# HPA status
kubectl get hpa -n safety-event-system

# Detailed HPA information
kubectl describe hpa api-hpa -n safety-event-system
kubectl describe hpa frontend-hpa -n safety-event-system

# HPA metrics
kubectl get hpa api-hpa -n safety-event-system -o yaml
```

### View Events

```bash
# All events
kubectl get events -n safety-event-system --sort-by='.lastTimestamp'

# Scaling events only
kubectl get events -n safety-event-system --field-selector reason=ScalingReplicaSet
```

## Cleanup

### Delete Application

```bash
# Delete all resources in namespace
kubectl delete namespace safety-event-system
```

### Delete GKE Cluster

```bash
# Delete cluster (careful: this deletes everything!)
gcloud container clusters delete safety-event-cluster --region=us-central1
```

## Troubleshooting

### Pods Not Scaling

**Check HPA status:**
```bash
kubectl describe hpa api-hpa -n safety-event-system
```

**Common issues:**
- Metrics server not installed: `kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml`
- Resource requests not defined: Check pod specs
- Not enough cluster resources: Scale cluster nodes

### LoadBalancer Pending

**Check service:**
```bash
kubectl describe service api-service -n safety-event-system
```

**Solution:** Wait 2-5 minutes for GCP to provision LoadBalancer

### Pods Failing to Start

**Check pod status:**
```bash
kubectl describe pod <pod-name> -n safety-event-system
kubectl logs <pod-name> -n safety-event-system
```

**Common issues:**
- Image pull errors: Check GCR permissions
- Secret missing: Re-create `gcp-credentials` secret
- Resource limits: Adjust requests/limits in deployment

## Cost Optimization

### Development/Testing

```yaml
# Reduce cluster size
--num-nodes=2
--machine-type=e2-standard-2

# Reduce replicas
API: minReplicas=1, maxReplicas=3
Frontend: minReplicas=1, maxReplicas=2
```

### Production

```yaml
# Current configuration (recommended)
--num-nodes=3
--machine-type=e2-standard-4
API: minReplicas=3, maxReplicas=10
Frontend: minReplicas=2, maxReplicas=6
```

## Best Practices

1. **Always use namespaces** for resource isolation
2. **Set resource requests and limits** for all containers
3. **Use HPA** for automatic scaling
4. **Use StatefulSets** for stateful services (ChromaDB)
5. **Configure health checks** (liveness and readiness probes)
6. **Use secrets** for sensitive data
7. **Monitor metrics** regularly
8. **Set appropriate scaling policies** (stabilization windows)

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Managing Resources](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)

# Kubernetes Deployment Verification Checklist

## Pre-Deployment Checks ✅

- [x] GCP project configured correctly (`apcomp215-group88`)
- [x] Kubernetes Engine API enabled
- [x] Deployment scripts executable (`chmod +x`)
- [x] CPU quota sufficient (adjusted to e2-standard-2, 2 nodes)

## Cluster Creation Verification

Run the following commands to verify cluster status:

```bash
# View cluster information
gcloud container clusters describe safety-event-cluster --region=us-central1

# Get cluster credentials
gcloud container clusters get-credentials safety-event-cluster --region=us-central1

# View nodes
kubectl get nodes

# Verify node specifications
kubectl describe nodes | grep -E "Name:|machine-type|cpu|memory"
```

**Expected Results:**
- 6 nodes (2 per zone × 3 zones)
- Machine type: e2-standard-2
- Each node: 2 CPUs, 8GB RAM

## Application Deployment Verification

### 1. Namespace Checkace Check
```bash
kubectl get namespace safety-event-system
```
**Expected:** `safety-event-system   Active   <time>`

### 2. ConfigMap and Secret Check
```bash
kubectl get configmap -n safety-event-system
kubectl get secret -n safety-event-system
```
**Expected:** See `app-config` and `gcp-credentials`

### 3. Deployment Status Checkment Status Check
```bash
kubectl get deployments -n safety-event-system
```
**Expected Output:**
```
NAME                 READY   UP-TO-DATE   AVAILABLE   AGE
api-deployment       3/3     3            3           <time>
frontend-deployment  2/2     2            2           <time>
```

### 4. StatefulSet Check (ChromaDB)DB)
```bash
kubectl get statefulset -n safety-event-system
```
**Expected Output:**
```
NAME       READY   AGE
chromadb   1/1     <time>
```

### 5. Pod Status Check
```bash
kubectl get pods -n safety-event-system
```
**Expected:** All Pods status `Running`
- 3 API pods
- 2 Frontend pods
- 1 ChromaDB pod

### 6. Service Checkeck
```bash
kubectl get services -n safety-event-system
```
**Expected Output:**
```
NAME                TYPE           EXTERNAL-IP     PORT(S)
api-service         LoadBalancer   <pending/IP>    9000:xxxxx/TCP
frontend-service    LoadBalancer   <pending/IP>    80:xxxxx/TCP
chromadb-service    ClusterIP      <internal-IP>   8000/TCP
```

### 7. HPA Checkeck
```bash
kubectl get hpa -n safety-event-system
```
**Expected Output:**
```
NAME            REFERENCE                   TARGETS         MINPODS   MAXPODS
api-hpa         Deployment/api-deployment   <unknown>/70%   3         10
frontend-hpa    Deployment/frontend-deployment <unknown>/70% 2        6
```

**Note:** Initial TARGETS may show `<unknown>`, wait 1-2 minutes for actual CPU/memory usage to display

## Health Check Verification

### 1. Pod Log CheckCheck
```bash
# API logs
kubectl logs -l app=safety-event-api -n safety-event-system --tail=50

# Frontend logs
kubectl logs -l app=safety-event-frontend -n safety-event-system --tail=50

# ChromaDB logs
kubectl logs statefulset/chromadb -n safety-event-system --tail=50
```

**Expected:** No ERROR or FATAL logs, application starts normally

### 2. Health Endpoint Test Endpoint Test
```bash
# Get API external IP
API_IP=$(kubectl get service api-service -n safety-event-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test health endpoint
curl http://${API_IP}:9000/api/v1/health
```
**Expected Output:** `{"status":"healthy"}`

### 3. Frontend Access Testss Test
```bash
# Get Frontend external IP
FRONTEND_IP=$(kubectl get service frontend-service -n safety-event-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Access in browser
echo "Frontend URL: http://${FRONTEND_IP}"
```
**Expected:** Able to access login page

## Resource Usage Verification

### 1. Node Resource Usageesource Usage
```bash
kubectl top nodes
```
**Expected:** Each node CPU/memory usage < 80%

### 2. Pod Resource Usage
```bash
kubectl top pods -n safety-event-system
```
**Expected:** 
- API pods: CPU < 250m, Memory < 512Mi
- Frontend pods: CPU < 100m, Memory < 256Mi
- ChromaDB: CPU < 500m, Memory < 1Gi

### 3. PersistentVolume Checkeck
```bash
kubectl get pv
kubectl get pvc -n safety-event-system
```
**Expected:** ChromaDB PVC status is `Bound`, capacity 10Gi

## Auto-Scaling Verification

### 1. Initial Stateial State
```bash
kubectl get pods -l app=safety-event-api -n safety-event-system
```
**Expected:** Exactly 3 API pods (minimum replicas)

### 2. Run Load Test
```bash
./k8s/load-test.sh
```

### 3. Observe Scaling
While the load test is running, run in another terminal:t is running, run in another terminal:
```bash
watch -n 5 'kubectl get hpa -n safety-event-system && kubectl get pods -l app=safety-event-api -n safety-event-system'
```

**Expected Behavior:**

| Time | Load | CPU Usage | Pod Count | Description |
|------|------|-----------|-----------|-------------|
| 0-30s | Low | <30% | 3 | Baseline |
| 30s-2min | Medium | 70-80% | 3→5-6 | Scale up triggered |
| 2-4min | High | 85-95% | 6→8-10 | Scale to maximum |
| 5-10min after stop | None | <20% | 8-10→3 | Scale back to minimum |

### 4. Verify Scaling Events Scaling Events
```bash
kubectl get events -n safety-event-system --sort-by='.lastTimestamp' | grep -i scale
```
**Expected:** See `ScaledUpReplica` and `ScaledDownReplica` events

## Network Connectivity Verification

### 1. Inter-Pod Communication Test Communication Test
```bash
# Enter API pod
kubectl exec -it deployment/api-deployment -n safety-event-system -- /bin/bash

# Test connection to ChromaDB
curl http://chromadb-service:8000/api/v1

# Exit
exit
```

### 2. Frontend to API Connectiononnection
```bash
# Enter Frontend pod
kubectl exec -it deployment/frontend-deployment -n safety-event-system -- /bin/sh

# Test API connection
curl http://api-service:9000/api/v1/health

# Exit
exit
```

## Troubleshooting Common Issues

### Issue 1: Pod Stuck in Pendingn Pending
```bash
kubectl describe pod <pod-name> -n safety-event-system
```
**Possible Causes:**
- Insufficient node resources → Adjust node count or resource limits
- PVC cannot bind → Check storage configuration

### Issue 2: LoadBalancer Stuck in Pendingn Pending
```bash
kubectl describe service api-service -n safety-event-system
```
**Solution:** Wait 2-5 minutes, GCP needs time to allocate external IP

### Issue 3: HPA Shows <unknown>known>
```bash
kubectl get apiservice v1beta1.metrics.k8s.io -o yaml
```
**Solution:** Confirm metrics-server is running
```bash
kubectl get deployment metrics-server -n kube-system
```

### Issue 4: Image Pull Failed Failed
```bash
kubectl describe pod <pod-name> -n safety-event-system
```
**Solution:** 
- Confirm image is pushed to GCR
- Check GCP permissions configuration

## Complete Verification Script

Create and run complete verification: run complete verification:

```bash
#!/bin/bash
# Save as verify-deployment.sh

echo "=== Kubernetes Deployment Verification ==="
echo ""

echo "1. Cluster Information:"
kubectl cluster-info
echo ""

echo "2. Node Status:"
kubectl get nodes
echo ""

echo "3. Namespace:"
kubectl get namespace safety-event-system
echo ""

echo "4. All Resources:"
kubectl get all -n safety-event-system
echo ""

echo "5. HPA Status:"
kubectl get hpa -n safety-event-system
echo ""

echo "6. PVC Status:"
kubectl get pvc -n safety-event-system
echo ""

echo "7. Service External IPs:"
kubectl get services -n safety-event-system
echo ""

echo "8. Pod Resource Usage:"
kubectl top pods -n safety-event-system 2>/dev/null || echo "Metrics not ready yet"
echo ""

echo "=== Verification Complete ==="ion Complete ==="
```

## Cleanup Resources

If you need to delete the deployment:

```bash
# Delete application (keep cluster)
kubectl delete namespace safety-event-system

# Delete entire cluster
gcloud container clusters delete safety-event-cluster --region=us-central1
```

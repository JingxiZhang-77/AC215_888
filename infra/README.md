# Pulumi Infrastructure as Code

This directory contains Pulumi code to automate the provisioning and deployment of the entire Safety Event Classification System infrastructure.

## Overview

This Pulumi program automates:
- **GKE Cluster**: Google Kubernetes Engine cluster with auto-scaling node pools
- **Networking**: LoadBalancer services for external access
- **Storage**: Persistent volumes for ChromaDB
- **Configurations**: Secrets, ConfigMaps, and environment variables
- **Application Deployment**: API backend, Frontend, and ChromaDB
- **Auto-scaling**: Horizontal Pod Autoscalers for dynamic scaling

## Prerequisites

1. **Install Pulumi**:
   ```bash
   curl -fsSL https://get.pulumi.com | sh
   ```

2. **Install Python dependencies**:
   ```bash
   cd infra
   pip install -r requirements.txt
   ```

3. **Authenticate with GCP**:
   ```bash
   gcloud auth application-default login
   gcloud config set project apcomp215-group88
   ```

4. **Install gke-gcloud-auth-plugin**:
   ```bash
   gcloud components install gke-gcloud-auth-plugin
   ```

5. **Service Account Key**: Ensure `../secrets/llm-service-account.json` exists

## Quick Start

### Initialize Pulumi Stack

```bash
cd infra

# Login to Pulumi (use local backend)
pulumi login --local

# Or use Pulumi Cloud
pulumi login

# Select or create stack
pulumi stack select dev
# or
pulumi stack init dev
```

### Deploy Infrastructure

```bash
# Preview changes
pulumi preview

# Deploy all resources
pulumi up

# Confirm deployment when prompted
```

This will create:
- GKE cluster with 2 nodes (e2-standard-2)
- Namespace `safety-event-system`
- Secrets for GCP credentials
- ChromaDB StatefulSet with persistent storage
- API backend deployment (3 replicas)
- Frontend deployment (2 replicas)
- LoadBalancer services for external access
- Horizontal Pod Autoscalers

### Check Deployment Status

```bash
# View outputs
pulumi stack output

# Get frontend URL
pulumi stack output frontend_url

# Get API URL
pulumi stack output api_url

# Get full stack information
pulumi stack
```

### Access the Application

After deployment completes, get the URLs:

```bash
# Frontend
echo "Frontend: $(pulumi stack output frontend_url)"

# API
echo "API: $(pulumi stack output api_url)"
echo "API Docs: $(pulumi stack output api_url)/docs"
```

### Update Application

After rebuilding and pushing Docker images:

```bash
# Refresh Pulumi to pick up new images
pulumi up --refresh

# Or force update with new images
pulumi up --replace "urn:pulumi:dev::safety-event-system-infra::kubernetes:apps/v1:Deployment::api-deployment"
```

## Configuration

### Stack Configuration Files

- `Pulumi.dev.yaml`: Development environment configuration
- `Pulumi.prod.yaml`: Production environment configuration

### Modify Configuration

```bash
# Set GCP project
pulumi config set gcp:project your-project-id

# Set GCP region
pulumi config set gcp:region us-central1

# Set service account path
pulumi config set gcpServiceAccountPath ../secrets/llm-service-account.json
```

## Infrastructure Components

### 1. GKE Cluster
- **Machine Type**: e2-standard-2 (2 vCPUs, 8GB RAM)
- **Initial Nodes**: 2 per zone (6 total in multi-zone)
- **Auto-scaling**: Enabled via GKE node pools
- **Version**: Latest stable GKE version

### 2. Kubernetes Resources

**Namespace**: `safety-event-system`
- Isolates all application resources
- Managed by Pulumi with labels

**Secrets**:
- `gcp-credentials`: GCP service account key for API access

**ConfigMaps**:
- `app-config`: Environment variables for all services

**Persistent Storage**:
- `chromadb-data`: 10Gi PVC for vector database

### 3. Application Services

**ChromaDB** (StatefulSet):
- 1 replica with persistent storage
- Internal ClusterIP service
- Health checks on `/api/v1`

**API Backend** (Deployment):
- 3 initial replicas
- Auto-scales: 3-10 pods based on CPU (70%) and Memory (80%)
- LoadBalancer service on port 9000
- Health checks on `/api/v1/health`

**Frontend** (Deployment):
- 2 initial replicas
- Auto-scales: 2-6 pods based on CPU and Memory
- LoadBalancer service on port 80
- Dynamic API URL configuration

### 4. Auto-scaling

**Horizontal Pod Autoscalers (HPA)**:
- API: 3-10 replicas (target: 70% CPU, 80% Memory)
- Frontend: 2-6 replicas (target: 70% CPU, 80% Memory)

## Operations

### View Resources

```bash
# List all resources
pulumi stack --show-urns

# View specific resource
pulumi stack export | grep -A 10 "api-deployment"
```

### Destroy Infrastructure

```bash
# Preview what will be destroyed
pulumi destroy --preview

# Destroy all resources
pulumi destroy

# Confirm when prompted
```

**Warning**: This will delete:
- GKE cluster and all nodes
- All Kubernetes resources
- Persistent volumes and data
- LoadBalancer IPs

### Update Stack

```bash
# Refresh state from cloud
pulumi refresh

# Update with new code changes
pulumi up

# Cancel an update
pulumi cancel
```

### Rollback

```bash
# View history
pulumi stack history

# Rollback to previous version
pulumi stack import <checkpoint-file>
```

## Troubleshooting

### Check Pod Status

```bash
# Get kubeconfig
pulumi stack output kubeconfig --show-secrets > /tmp/kubeconfig.yaml
export KUBECONFIG=/tmp/kubeconfig.yaml

# Check pods
kubectl get pods -n safety-event-system

# View logs
kubectl logs -l app=safety-event-api -n safety-event-system
```

### LoadBalancer IP Pending

If external IPs show "Pending...":
1. Wait 2-3 minutes for GCP to provision
2. Check GCP console for LoadBalancer creation
3. Verify project has LoadBalancer quota

### Authentication Issues

```bash
# Re-authenticate
gcloud auth application-default login

# Verify service account
gcloud auth list

# Check credentials file
ls -l ../secrets/llm-service-account.json
```

### Pulumi State Issues

```bash
# Backup state
pulumi stack export > backup.json

# Import state
pulumi stack import < backup.json

# Reset state (danger!)
pulumi stack rm dev --force
```

## Cost Management

**Estimated Monthly Costs**:
- GKE cluster: ~$150 (6 nodes × e2-standard-2)
- LoadBalancers: ~$20 (2 external IPs)
- Persistent storage: ~$2 (10Gi)
- **Total**: ~$172/month

**To minimize costs**:
```bash
# Destroy when not in use
pulumi destroy

# Or scale down
pulumi config set api-replicas 1
pulumi config set frontend-replicas 1
pulumi up
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Deploy with Pulumi
  uses: pulumi/actions@v4
  with:
    command: up
    stack-name: dev
    work-dir: infra
  env:
    PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
```

## Best Practices

1. **Use Stack References**: Separate infrastructure and application stacks
2. **Secret Management**: Use Pulumi secrets for sensitive data
3. **State Backup**: Regularly export stack state
4. **Version Control**: Commit Pulumi code, not state files
5. **Testing**: Use `pulumi preview` before every `pulumi up`
6. **Documentation**: Update this README when modifying infrastructure

## Resources

- [Pulumi Docs](https://www.pulumi.com/docs/)
- [Pulumi GCP Provider](https://www.pulumi.com/registry/packages/gcp/)
- [Pulumi Kubernetes Provider](https://www.pulumi.com/registry/packages/kubernetes/)
- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)

## Support

For issues or questions:
1. Check Pulumi logs: `pulumi logs`
2. Verify GCP resources in console
3. Review Kubernetes events: `kubectl get events -n safety-event-system`
4. Contact DevOps team or create GitHub issue

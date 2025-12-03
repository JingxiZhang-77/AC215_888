"""
Pulumi Infrastructure as Code for Safety Event Classification System
Automates provisioning and deployment of GKE cluster and application
"""

import pulumi
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s
from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.core.v1 import (
    Service, ServiceSpecArgs, ServicePortArgs,
    Namespace, Secret, ConfigMap, PersistentVolumeClaim,
    ContainerArgs, ContainerPortArgs, EnvVarArgs, ResourceRequirementsArgs,
    PodSpecArgs, PodTemplateSpecArgs, LabelSelectorArgs,
    VolumeArgs, VolumeMountArgs, SecretVolumeSourceArgs, PersistentVolumeClaimVolumeSourceArgs,
    ProbeArgs, HTTPGetActionArgs
)
from pulumi_kubernetes.meta.v1 import ObjectMetaArgs
from pulumi_kubernetes.autoscaling.v2 import (
    HorizontalPodAutoscaler, HorizontalPodAutoscalerSpecArgs,
    MetricSpecArgs, ResourceMetricSourceArgs, MetricTargetArgs
)
from pulumi_kubernetes.apps.v1 import StatefulSet, StatefulSetSpecArgs
import base64

# Get configuration
config = pulumi.Config()
gcp_config = pulumi.Config("gcp")
project = gcp_config.require("project")
region = gcp_config.require("region")
service_account_path = config.get("gcpServiceAccountPath") or "../secrets/llm-service-account.json"

# Read GCP service account key
with open(service_account_path, 'r') as f:
    gcp_key_content = f.read()

# Create GKE cluster
cluster = gcp.container.Cluster(
    "safety-event-cluster",
    name="safety-event-cluster",
    location=region,
    initial_node_count=2,
    node_config=gcp.container.ClusterNodeConfigArgs(
        machine_type="e2-standard-2",
        oauth_scopes=[
            "https://www.googleapis.com/auth/cloud-platform",
        ],
    ),
    remove_default_node_pool=False,
    min_master_version="latest",
)

# Create a Kubernetes provider instance that uses our cluster
k8s_provider = k8s.Provider(
    "gke-k8s",
    kubeconfig=pulumi.Output.all(cluster.name, cluster.endpoint, cluster.master_auth).apply(
        lambda args: f"""apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {args[2].cluster_ca_certificate}
    server: https://{args[1]}
  name: {args[0]}
contexts:
- context:
    cluster: {args[0]}
    user: {args[0]}
  name: {args[0]}
current-context: {args[0]}
kind: Config
preferences: {{}}
users:
- name: {args[0]}
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: gke-gcloud-auth-plugin
      installHint: Install gke-gcloud-auth-plugin for use with kubectl by following
        https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl#install_plugin
      provideClusterInfo: true
"""
    ),
)

# Create namespace
namespace = Namespace(
    "safety-event-system",
    metadata=ObjectMetaArgs(
        name="safety-event-system",
        labels={
            "name": "safety-event-system",
            "managed-by": "pulumi",
        },
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)

# Create secret for GCP credentials
gcp_secret = Secret(
    "gcp-credentials",
    metadata=ObjectMetaArgs(
        name="gcp-credentials",
        namespace=namespace.metadata.name,
    ),
    string_data={
        "key.json": gcp_key_content,
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[namespace]),
)

# Create ConfigMap
config_map = ConfigMap(
    "app-config",
    metadata=ObjectMetaArgs(
        name="app-config",
        namespace=namespace.metadata.name,
    ),
    data={
        "GCP_PROJECT": project,
        "GCP_REGION": region,
        "GOOGLE_APPLICATION_CREDENTIALS": "/secrets/key.json",
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[namespace]),
)

# ChromaDB StatefulSet
chromadb_pvc = PersistentVolumeClaim(
    "chromadb-data",
    metadata=ObjectMetaArgs(
        name="chromadb-data",
        namespace=namespace.metadata.name,
    ),
    spec={
        "accessModes": ["ReadWriteOnce"],
        "resources": {
            "requests": {
                "storage": "10Gi",
            },
        },
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[namespace]),
)

chromadb_statefulset = StatefulSet(
    "chromadb",
    metadata=ObjectMetaArgs(
        name="chromadb",
        namespace=namespace.metadata.name,
        labels={"app": "chromadb"},
    ),
    spec=StatefulSetSpecArgs(
        service_name="chromadb-service",
        replicas=1,
        selector=LabelSelectorArgs(
            match_labels={"app": "chromadb"},
        ),
        template=PodTemplateSpecArgs(
            metadata=ObjectMetaArgs(
                labels={"app": "chromadb"},
            ),
            spec=PodSpecArgs(
                containers=[
                    ContainerArgs(
                        name="chromadb",
                        image="chromadb/chroma:latest",
                        ports=[ContainerPortArgs(container_port=8000, name="http")],
                        env=[
                            EnvVarArgs(name="IS_PERSISTENT", value="TRUE"),
                            EnvVarArgs(name="ANONYMIZED_TELEMETRY", value="FALSE"),
                        ],
                        volume_mounts=[
                            VolumeMountArgs(
                                name="chromadb-data",
                                mount_path="/chroma/chroma",
                            ),
                        ],
                        resources=ResourceRequirementsArgs(
                            requests={"memory": "512Mi", "cpu": "250m"},
                            limits={"memory": "1Gi", "cpu": "500m"},
                        ),
                        liveness_probe=ProbeArgs(
                            http_get=HTTPGetActionArgs(path="/api/v1", port=8000),
                            initial_delay_seconds=30,
                            period_seconds=10,
                        ),
                        readiness_probe=ProbeArgs(
                            http_get=HTTPGetActionArgs(path="/api/v1", port=8000),
                            initial_delay_seconds=20,
                            period_seconds=5,
                        ),
                    ),
                ],
                volumes=[
                    VolumeArgs(
                        name="chromadb-data",
                        persistent_volume_claim=PersistentVolumeClaimVolumeSourceArgs(
                            claim_name="chromadb-data",
                        ),
                    ),
                ],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[namespace, chromadb_pvc]),
)

chromadb_service = Service(
    "chromadb-service",
    metadata=ObjectMetaArgs(
        name="chromadb-service",
        namespace=namespace.metadata.name,
        labels={"app": "chromadb"},
    ),
    spec=ServiceSpecArgs(
        type="ClusterIP",
        selector={"app": "chromadb"},
        ports=[ServicePortArgs(port=8000, target_port=8000, protocol="TCP", name="http")],
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[namespace]),
)

# API Backend Deployment
api_deployment = Deployment(
    "api-deployment",
    metadata=ObjectMetaArgs(
        name="api-deployment",
        namespace=namespace.metadata.name,
        labels={"app": "safety-event-api", "tier": "backend"},
    ),
    spec=DeploymentSpecArgs(
        replicas=3,
        selector=LabelSelectorArgs(
            match_labels={"app": "safety-event-api"},
        ),
        template=PodTemplateSpecArgs(
            metadata=ObjectMetaArgs(
                labels={"app": "safety-event-api", "tier": "backend"},
            ),
            spec=PodSpecArgs(
                containers=[
                    ContainerArgs(
                        name="api",
                        image="gcr.io/apcomp215-group88/safety-event-api:latest",
                        image_pull_policy="Always",
                        command=[
                            "uvicorn",
                            "service:app",
                            "--host=0.0.0.0",
                            "--port=9000",
                        ],
                        ports=[ContainerPortArgs(container_port=9000, name="http")],
                        env=[
                            EnvVarArgs(name="GCP_PROJECT", value=project),
                            EnvVarArgs(name="GCP_REGION", value=region),
                            EnvVarArgs(name="GOOGLE_APPLICATION_CREDENTIALS", value="/secrets/key.json"),
                            EnvVarArgs(name="CHROMADB_HOST", value="chromadb-service"),
                            EnvVarArgs(name="CHROMADB_PORT", value="8000"),
                        ],
                        volume_mounts=[
                            VolumeMountArgs(
                                name="gcp-credentials",
                                mount_path="/secrets",
                                read_only=True,
                            ),
                        ],
                        resources=ResourceRequirementsArgs(
                            requests={"memory": "512Mi", "cpu": "250m"},
                            limits={"memory": "2Gi", "cpu": "1000m"},
                        ),
                        liveness_probe=ProbeArgs(
                            http_get=HTTPGetActionArgs(path="/api/v1/health", port=9000),
                            initial_delay_seconds=30,
                            period_seconds=10,
                        ),
                        readiness_probe=ProbeArgs(
                            http_get=HTTPGetActionArgs(path="/api/v1/health", port=9000),
                            initial_delay_seconds=20,
                            period_seconds=5,
                        ),
                    ),
                ],
                volumes=[
                    VolumeArgs(
                        name="gcp-credentials",
                        secret=SecretVolumeSourceArgs(
                            secret_name="gcp-credentials",
                        ),
                    ),
                ],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[namespace, gcp_secret]),
)

api_service = Service(
    "api-service",
    metadata=ObjectMetaArgs(
        name="api-service",
        namespace=namespace.metadata.name,
        labels={"app": "safety-event-api"},
    ),
    spec=ServiceSpecArgs(
        type="LoadBalancer",
        selector={"app": "safety-event-api"},
        ports=[ServicePortArgs(port=9000, target_port=9000, protocol="TCP", name="http")],
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[namespace]),
)

# Frontend Deployment
frontend_deployment = Deployment(
    "frontend-deployment",
    metadata=ObjectMetaArgs(
        name="frontend-deployment",
        namespace=namespace.metadata.name,
        labels={"app": "safety-event-frontend", "tier": "frontend"},
    ),
    spec=DeploymentSpecArgs(
        replicas=2,
        selector=LabelSelectorArgs(
            match_labels={"app": "safety-event-frontend"},
        ),
        template=PodTemplateSpecArgs(
            metadata=ObjectMetaArgs(
                labels={"app": "safety-event-frontend", "tier": "frontend"},
            ),
            spec=PodSpecArgs(
                containers=[
                    ContainerArgs(
                        name="frontend",
                        image="gcr.io/apcomp215-group88/safety-event-frontend:latest",
                        image_pull_policy="Always",
                        ports=[ContainerPortArgs(container_port=3001, name="http")],
                        env=[
                            # Note: API URL will be set during build via .env.production
                            # For runtime override, use external LoadBalancer IP
                            EnvVarArgs(
                                name="NEXT_PUBLIC_API_URL",
                                value=api_service.status.apply(
                                    lambda status: f"http://{status.load_balancer.ingress[0].ip}:9000/api/v1"
                                    if status.load_balancer and status.load_balancer.ingress
                                    else "http://api-service:9000/api/v1"
                                ),
                            ),
                        ],
                        resources=ResourceRequirementsArgs(
                            requests={"memory": "256Mi", "cpu": "100m"},
                            limits={"memory": "512Mi", "cpu": "500m"},
                        ),
                        liveness_probe=ProbeArgs(
                            http_get=HTTPGetActionArgs(path="/", port=3001),
                            initial_delay_seconds=30,
                            period_seconds=10,
                        ),
                        readiness_probe=ProbeArgs(
                            http_get=HTTPGetActionArgs(path="/", port=3001),
                            initial_delay_seconds=20,
                            period_seconds=5,
                        ),
                    ),
                ],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[namespace, api_service]),
)

frontend_service = Service(
    "frontend-service",
    metadata=ObjectMetaArgs(
        name="frontend-service",
        namespace=namespace.metadata.name,
        labels={"app": "safety-event-frontend"},
    ),
    spec=ServiceSpecArgs(
        type="LoadBalancer",
        selector={"app": "safety-event-frontend"},
        ports=[ServicePortArgs(port=80, target_port=3001, protocol="TCP", name="http")],
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[namespace]),
)

# Horizontal Pod Autoscalers
api_hpa = HorizontalPodAutoscaler(
    "api-hpa",
    metadata=ObjectMetaArgs(
        name="api-hpa",
        namespace=namespace.metadata.name,
    ),
    spec=HorizontalPodAutoscalerSpecArgs(
        scale_target_ref={
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "name": "api-deployment",
        },
        min_replicas=3,
        max_replicas=10,
        metrics=[
            MetricSpecArgs(
                type="Resource",
                resource=ResourceMetricSourceArgs(
                    name="cpu",
                    target=MetricTargetArgs(
                        type="Utilization",
                        average_utilization=70,
                    ),
                ),
            ),
            MetricSpecArgs(
                type="Resource",
                resource=ResourceMetricSourceArgs(
                    name="memory",
                    target=MetricTargetArgs(
                        type="Utilization",
                        average_utilization=80,
                    ),
                ),
            ),
        ],
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[namespace, api_deployment]),
)

frontend_hpa = HorizontalPodAutoscaler(
    "frontend-hpa",
    metadata=ObjectMetaArgs(
        name="frontend-hpa",
        namespace=namespace.metadata.name,
    ),
    spec=HorizontalPodAutoscalerSpecArgs(
        scale_target_ref={
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "name": "frontend-deployment",
        },
        min_replicas=2,
        max_replicas=6,
        metrics=[
            MetricSpecArgs(
                type="Resource",
                resource=ResourceMetricSourceArgs(
                    name="cpu",
                    target=MetricTargetArgs(
                        type="Utilization",
                        average_utilization=70,
                    ),
                ),
            ),
            MetricSpecArgs(
                type="Resource",
                resource=ResourceMetricSourceArgs(
                    name="memory",
                    target=MetricTargetArgs(
                        type="Utilization",
                        average_utilization=80,
                    ),
                ),
            ),
        ],
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[namespace, frontend_deployment]),
)

# Export important values
pulumi.export("cluster_name", cluster.name)
pulumi.export("cluster_endpoint", cluster.endpoint)
pulumi.export("kubeconfig", pulumi.Output.secret(k8s_provider.kubeconfig))
pulumi.export("namespace", namespace.metadata.name)
pulumi.export("api_service_ip", api_service.status.apply(
    lambda status: status.load_balancer.ingress[0].ip
    if status.load_balancer and status.load_balancer.ingress
    else "Pending..."
))
pulumi.export("frontend_service_ip", frontend_service.status.apply(
    lambda status: status.load_balancer.ingress[0].ip
    if status.load_balancer and status.load_balancer.ingress
    else "Pending..."
))
pulumi.export("api_url", api_service.status.apply(
    lambda status: f"http://{status.load_balancer.ingress[0].ip}:9000"
    if status.load_balancer and status.load_balancer.ingress
    else "Pending..."
))
pulumi.export("frontend_url", frontend_service.status.apply(
    lambda status: f"http://{status.load_balancer.ingress[0].ip}"
    if status.load_balancer and status.load_balancer.ingress
    else "Pending..."
))

import os
import pulumi
import pulumi_docker_build as docker_build
from pulumi_gcp import artifactregistry
from pulumi import CustomTimeouts
import datetime
import json
import base64

# 🔧 Get project info
project = pulumi.Config("gcp").require("project")
location = os.environ["GCP_REGION"]
region = "us-central1"

# 🕒 Timestamp for tagging
timestamp_tag = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
repository_name = "group88"
registry_url = f"{region}-docker.pkg.dev/{project}/{repository_name}"

# Read GCP service account for registry authentication
with open("../../secrets/deployment.json", "r") as f:
    gcp_creds = json.load(f) 

# Create registry auth for Artifact Registry
registry_auth = docker_build.RegistryArgs(
    address=f"{region}-docker.pkg.dev",
    username="_json_key",
    password=json.dumps(gcp_creds),
)

# Docker Build + Push -> API Service
image_config = {
    "image_name": "group88-api-service",
    "context_path": "../src/api",
    "dockerfile": "Dockerfile"
}
api_service_image = docker_build.Image(
    f"build-{image_config["image_name"]}",
    tags=[pulumi.Output.concat(registry_url, "/", image_config["image_name"], ":", timestamp_tag)],
    context=docker_build.BuildContextArgs(location=image_config["context_path"]),
    dockerfile={"location": f"{image_config["context_path"]}/{image_config["dockerfile"]}"},
    platforms=[docker_build.Platform.LINUX_AMD64],
    push=True,
    registries=[registry_auth],
    opts=pulumi.ResourceOptions(custom_timeouts=CustomTimeouts(create="30m"),
                                retain_on_delete=True)
)
# Export references to stack
pulumi.export("group88-api-service-ref", api_service_image.ref)
pulumi.export("group88-api-service-tags", api_service_image.tags)

# Docker Build + Push -> Frontend
image_config = {
    "image_name": "group88-frontend-react",
    "context_path": "../src/frontend-react",
    "dockerfile": "Dockerfile"
}
frontend_image = docker_build.Image(
    f"build-{image_config["image_name"]}",
    tags=[pulumi.Output.concat(registry_url, "/", image_config["image_name"], ":", timestamp_tag)],
    context=docker_build.BuildContextArgs(location=image_config["context_path"]),
    dockerfile={"location": f"{image_config["context_path"]}/{image_config["dockerfile"]}"},
    platforms=[docker_build.Platform.LINUX_AMD64],
    push=True,
    registries=[registry_auth],
    opts=pulumi.ResourceOptions(custom_timeouts=CustomTimeouts(create="30m"),
                                retain_on_delete=True)
)
pulumi.export("group88-frontend-react-ref", frontend_image.ref)
pulumi.export("group88-frontend-react-tags", frontend_image.tags)

# Docker Build + Push -> vector-db-cli
image_config = {
    "image_name": "group88-vector-db-cli",
    "context_path": "../src/vector-db",
    "dockerfile": "Dockerfile"
}
vector_db_cli_image = docker_build.Image(
    f"build-{image_config["image_name"]}",
    tags=[pulumi.Output.concat(registry_url, "/", image_config["image_name"], ":", timestamp_tag)],
    context=docker_build.BuildContextArgs(location=image_config["context_path"]),
    dockerfile={"location": f"{image_config["context_path"]}/{image_config["dockerfile"]}"},
    platforms=[docker_build.Platform.LINUX_AMD64],
    push=True,
    registries=[registry_auth],
    opts=pulumi.ResourceOptions(custom_timeouts=CustomTimeouts(create="30m"),
                                retain_on_delete=True)
)
# Export references to stack
pulumi.export("group88-vector-db-cli-ref", vector_db_cli_image.ref)
pulumi.export("group88-vector-db-cli-tags", vector_db_cli_image.tags)
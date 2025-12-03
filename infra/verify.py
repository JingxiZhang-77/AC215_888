#!/usr/bin/env python3
"""
Pulumi Infrastructure Verification Script
Checks if all required components are properly defined
"""

import os
import sys
import re

def check_file_exists(filename):
    """Check if a file exists"""
    return os.path.isfile(filename)

def check_code_contains(filename, patterns):
    """Check if code contains specific patterns"""
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        results = {}
        for name, pattern in patterns.items():
            if isinstance(pattern, list):
                # Check if any pattern matches
                results[name] = any(re.search(p, content) for p in pattern)
            else:
                results[name] = bool(re.search(pattern, content))
        return results
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return {}

def main():
    print("="*60)
    print("Pulumi Infrastructure Code Verification")
    print("="*60)
    print()
    
    passed = 0
    failed = 0
    warnings = 0
    
    # Check file structure
    print("1. File Structure")
    print("-" * 60)
    
    required_files = {
        "__main__.py": "Main Pulumi program",
        "Pulumi.yaml": "Project configuration",
        "Pulumi.dev.yaml": "Dev stack config",
        "Pulumi.prod.yaml": "Prod stack config",
        "requirements.txt": "Python dependencies",
        "README.md": "Documentation",
        ".gitignore": "Git ignore rules"
    }
    
    for filename, description in required_files.items():
        if check_file_exists(filename):
            print(f"  ✓ {filename:25} - {description}")
            passed += 1
        else:
            print(f"  ✗ {filename:25} - {description} [MISSING]")
            failed += 1
    
    print()
    
    # Check Python syntax
    print("2. Python Syntax Validation")
    print("-" * 60)
    
    try:
        import py_compile
        py_compile.compile('__main__.py', doraise=True)
        print("  ✓ Python syntax is valid")
        passed += 1
    except py_compile.PyCompileError as e:
        print(f"  ✗ Python syntax error: {e}")
        failed += 1
    
    print()
    
    # Check infrastructure components
    print("3. Infrastructure Components")
    print("-" * 60)
    
    components = {
        "GCP Provider": r"import pulumi_gcp",
        "Kubernetes Provider": r"import pulumi_kubernetes",
        "GKE Cluster": r"gcp\.container\.Cluster\(",
        "Namespace": r'Namespace\(\s*["\']safety-event-system',
        "GCP Secret": r'Secret\(\s*["\']gcp-credentials',
        "ConfigMap": r"ConfigMap\(",
        "API Deployment": r'Deployment\(\s*["\']api-deployment',
        "Frontend Deployment": r'Deployment\(\s*["\']frontend-deployment',
        "ChromaDB StatefulSet": r'StatefulSet\(\s*["\']chromadb',
        "Persistent Storage": r"PersistentVolumeClaim\(",
        "API Service (LoadBalancer)": r'Service\(\s*["\']api-service',
        "Frontend Service (LoadBalancer)": r'Service\(\s*["\']frontend-service',
        "ChromaDB Service": r'Service\(\s*["\']chromadb-service',
        "API HPA": r'HorizontalPodAutoscaler\(\s*["\']api-hpa',
        "Frontend HPA": r'HorizontalPodAutoscaler\(\s*["\']frontend-hpa',
        "Pulumi Exports": r"pulumi\.export\(",
    }
    
    results = check_code_contains("__main__.py", components)
    
    for component, found in results.items():
        if found:
            print(f"  ✓ {component}")
            passed += 1
        else:
            print(f"  ✗ {component} [NOT FOUND]")
            failed += 1
    
    print()
    
    # Check configuration
    print("4. Configuration Validation")
    print("-" * 60)
    
    config_checks = {
        "Project name": r"name:\s*safety-event-system-infra",
        "Python runtime": r"runtime:\s*python",
        "GCP project config": r"gcp:project",
        "GCP region config": r"gcp:region",
        "Service account path": r"gcpServiceAccountPath",
    }
    
    # Check Pulumi.yaml
    yaml_results = check_code_contains("Pulumi.yaml", {
        "project": config_checks["Project name"],
        "runtime": config_checks["Python runtime"],
    })
    
    for key, found in yaml_results.items():
        if found:
            print(f"  ✓ {key.capitalize()} in Pulumi.yaml")
            passed += 1
        else:
            print(f"  ✗ {key.capitalize()} in Pulumi.yaml [MISSING]")
            failed += 1
    
    # Check stack configs
    dev_results = check_code_contains("Pulumi.dev.yaml", {
        "gcp_project": config_checks["GCP project config"],
        "gcp_region": config_checks["GCP region config"],
        "sa_path": config_checks["Service account path"],
    })
    
    for key, found in dev_results.items():
        if found:
            print(f"  ✓ {key} in Pulumi.dev.yaml")
            passed += 1
        else:
            print(f"  ✗ {key} in Pulumi.dev.yaml [MISSING]")
            failed += 1
    
    print()
    
    # Check dependencies
    print("5. Python Dependencies")
    print("-" * 60)
    
    deps = {
        "pulumi": r"pulumi>=",
        "pulumi-gcp": r"pulumi-gcp>=",
        "pulumi-kubernetes": r"pulumi-kubernetes>=",
    }
    
    dep_results = check_code_contains("requirements.txt", deps)
    
    for dep, found in dep_results.items():
        if found:
            print(f"  ✓ {dep}")
            passed += 1
        else:
            print(f"  ✗ {dep} [MISSING]")
            failed += 1
    
    print()
    
    # Check prerequisites
    print("6. System Prerequisites")
    print("-" * 60)
    
    prereqs = {
        "pulumi": "Pulumi CLI",
        "gcloud": "Google Cloud SDK",
        "python3": "Python 3",
    }
    
    for cmd, name in prereqs.items():
        if os.system(f"which {cmd} > /dev/null 2>&1") == 0:
            print(f"  ✓ {name} installed")
            passed += 1
        else:
            print(f"  ⚠ {name} not installed (may be required)")
            warnings += 1
    
    # Check service account
    sa_path = "../secrets/llm-service-account.json"
    if os.path.isfile(sa_path):
        print(f"  ✓ GCP service account key found")
        passed += 1
    else:
        print(f"  ⚠ GCP service account key not found at {sa_path}")
        warnings += 1
    
    print()
    
    # Resource count summary
    print("7. Resource Summary")
    print("-" * 60)
    
    try:
        with open("__main__.py", 'r') as f:
            content = f.read()
        
        resource_counts = {
            "GKE Clusters": len(re.findall(r'gcp\.container\.Cluster\(', content)),
            "Namespaces": len(re.findall(r'Namespace\(', content)),
            "Secrets": len(re.findall(r'Secret\(', content)),
            "ConfigMaps": len(re.findall(r'ConfigMap\(', content)),
            "Deployments": len(re.findall(r'Deployment\(', content)),
            "Services": len(re.findall(r'Service\(', content)),
            "StatefulSets": len(re.findall(r'StatefulSet\(', content)),
            "HPAs": len(re.findall(r'HorizontalPodAutoscaler\(', content)),
            "PVCs": len(re.findall(r'PersistentVolumeClaim\(', content)),
            "Exports": len(re.findall(r'pulumi\.export\(', content)),
        }
        
        for resource, count in resource_counts.items():
            print(f"  • {resource:20} : {count}")
        
        passed += 1
        
    except Exception as e:
        print(f"  ✗ Error counting resources: {e}")
        failed += 1
    
    print()
    
    # Final summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  ✓ Passed:   {passed}")
    print(f"  ✗ Failed:   {failed}")
    print(f"  ⚠ Warnings: {warnings}")
    print()
    
    if failed == 0:
        print("✅ All checks passed! Your Pulumi infrastructure is complete.")
        print()
        print("Next steps:")
        print("  1. Install Pulumi: curl -fsSL https://get.pulumi.com | sh")
        print("  2. Install dependencies: pip install -r requirements.txt")
        print("  3. Initialize: pulumi login --local")
        print("  4. Deploy: pulumi up")
        print()
        return 0
    else:
        print("❌ Some checks failed. Please review and fix the issues above.")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())

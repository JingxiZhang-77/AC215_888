# Kubernetes 部署验证清单

## 部署前检查 ✅

- [x] GCP 项目设置正确 (`apcomp215-group88`)
- [x] Kubernetes Engine API 已启用
- [x] 部署脚本可执行 (`chmod +x`)
- [x] CPU 配额足够 (调整为 e2-standard-2, 2 nodes)

## 集群创建验证

运行以下命令验证集群状态：

```bash
# 查看集群信息
gcloud container clusters describe safety-event-cluster --region=us-central1

# 获取集群凭证
gcloud container clusters get-credentials safety-event-cluster --region=us-central1

# 查看节点
kubectl get nodes

# 验证节点规格
kubectl describe nodes | grep -E "Name:|machine-type|cpu|memory"
```

**预期结果：**
- 6 个节点 (每个区域 2 个 × 3 区域)
- 机器类型: e2-standard-2
- 每个节点: 2 CPUs, 8GB RAM

## 应用部署验证

### 1. 命名空间检查
```bash
kubectl get namespace safety-event-system
```
**预期:** `safety-event-system   Active   <time>`

### 2. ConfigMap 和 Secret 检查
```bash
kubectl get configmap -n safety-event-system
kubectl get secret -n safety-event-system
```
**预期:** 看到 `app-config` 和 `gcp-credentials`

### 3. 部署状态检查
```bash
kubectl get deployments -n safety-event-system
```
**预期输出：**
```
NAME                 READY   UP-TO-DATE   AVAILABLE   AGE
api-deployment       3/3     3            3           <time>
frontend-deployment  2/2     2            2           <time>
```

### 4. StatefulSet 检查 (ChromaDB)
```bash
kubectl get statefulset -n safety-event-system
```
**预期输出：**
```
NAME       READY   AGE
chromadb   1/1     <time>
```

### 5. Pod 状态检查
```bash
kubectl get pods -n safety-event-system
```
**预期:** 所有 Pod 状态为 `Running`
- 3 个 API pods
- 2 个 Frontend pods
- 1 个 ChromaDB pod

### 6. Service 检查
```bash
kubectl get services -n safety-event-system
```
**预期输出：**
```
NAME                TYPE           EXTERNAL-IP     PORT(S)
api-service         LoadBalancer   <pending/IP>    9000:xxxxx/TCP
frontend-service    LoadBalancer   <pending/IP>    80:xxxxx/TCP
chromadb-service    ClusterIP      <internal-IP>   8000/TCP
```

### 7. HPA 检查
```bash
kubectl get hpa -n safety-event-system
```
**预期输出：**
```
NAME            REFERENCE                   TARGETS         MINPODS   MAXPODS
api-hpa         Deployment/api-deployment   <unknown>/70%   3         10
frontend-hpa    Deployment/frontend-deployment <unknown>/70% 2        6
```

**注意:** 初始 TARGETS 可能显示 `<unknown>`，等待 1-2 分钟后会显示实际 CPU/内存使用率

## 健康检查验证

### 1. Pod 日志检查
```bash
# API 日志
kubectl logs -l app=safety-event-api -n safety-event-system --tail=50

# Frontend 日志
kubectl logs -l app=safety-event-frontend -n safety-event-system --tail=50

# ChromaDB 日志
kubectl logs statefulset/chromadb -n safety-event-system --tail=50
```

**预期:** 没有 ERROR 或 FATAL 日志，应用正常启动

### 2. 健康端点测试
```bash
# 获取 API 外部 IP
API_IP=$(kubectl get service api-service -n safety-event-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# 测试健康端点
curl http://${API_IP}:9000/api/v1/health
```
**预期输出:** `{"status":"healthy"}`

### 3. Frontend 访问测试
```bash
# 获取 Frontend 外部 IP
FRONTEND_IP=$(kubectl get service frontend-service -n safety-event-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# 在浏览器中访问
echo "Frontend URL: http://${FRONTEND_IP}"
```
**预期:** 能够访问登录页面

## 资源使用验证

### 1. 节点资源使用
```bash
kubectl top nodes
```
**预期:** 每个节点 CPU/内存使用率 < 80%

### 2. Pod 资源使用
```bash
kubectl top pods -n safety-event-system
```
**预期:** 
- API pods: CPU < 250m, Memory < 512Mi
- Frontend pods: CPU < 100m, Memory < 256Mi
- ChromaDB: CPU < 500m, Memory < 1Gi

### 3. PersistentVolume 检查
```bash
kubectl get pv
kubectl get pvc -n safety-event-system
```
**预期:** ChromaDB 的 PVC 状态为 `Bound`，容量 10Gi

## 自动扩缩容验证

### 1. 初始状态
```bash
kubectl get pods -l app=safety-event-api -n safety-event-system
```
**预期:** 正好 3 个 API pods (最小副本数)

### 2. 运行负载测试
```bash
./k8s/load-test.sh
```

### 3. 观察扩容
在负载测试运行时，在另一个终端运行：
```bash
watch -n 5 'kubectl get hpa -n safety-event-system && kubectl get pods -l app=safety-event-api -n safety-event-system'
```

**预期行为：**

| 时间 | 负载 | CPU 使用率 | Pod 数量 | 说明 |
|------|------|-----------|---------|------|
| 0-30s | 低 | <30% | 3 | 基线状态 |
| 30s-2min | 中等 | 70-80% | 3→5-6 | 触发扩容 |
| 2-4min | 高 | 85-95% | 6→8-10 | 扩到最大 |
| 停止后 5-10min | 无 | <20% | 8-10→3 | 缩回最小 |

### 4. 验证扩容事件
```bash
kubectl get events -n safety-event-system --sort-by='.lastTimestamp' | grep -i scale
```
**预期:** 看到 `ScaledUpReplica` 和 `ScaledDownReplica` 事件

## 网络连接验证

### 1. Pod 间通信测试
```bash
# 进入 API pod
kubectl exec -it deployment/api-deployment -n safety-event-system -- /bin/bash

# 测试连接到 ChromaDB
curl http://chromadb-service:8000/api/v1

# 退出
exit
```

### 2. Frontend 到 API 连接
```bash
# 进入 Frontend pod
kubectl exec -it deployment/frontend-deployment -n safety-event-system -- /bin/sh

# 测试 API 连接
curl http://api-service:9000/api/v1/health

# 退出
exit
```

## 常见问题排查

### 问题 1: Pod 一直 Pending
```bash
kubectl describe pod <pod-name> -n safety-event-system
```
**可能原因:**
- 节点资源不足 → 调整节点数或资源限制
- PVC 无法绑定 → 检查存储配置

### 问题 2: LoadBalancer 一直 Pending
```bash
kubectl describe service api-service -n safety-event-system
```
**解决方案:** 等待 2-5 分钟，GCP 需要时间分配外部 IP

### 问题 3: HPA 显示 <unknown>
```bash
kubectl get apiservice v1beta1.metrics.k8s.io -o yaml
```
**解决方案:** 确认 metrics-server 正在运行
```bash
kubectl get deployment metrics-server -n kube-system
```

### 问题 4: Image Pull 失败
```bash
kubectl describe pod <pod-name> -n safety-event-system
```
**解决方案:** 
- 确认镜像已推送到 GCR
- 检查 GCP 权限配置

## 完整验证脚本

创建并运行完整验证：

```bash
#!/bin/bash
# 保存为 verify-deployment.sh

echo "=== Kubernetes 部署验证 ==="
echo ""

echo "1. 集群信息:"
kubectl cluster-info
echo ""

echo "2. 节点状态:"
kubectl get nodes
echo ""

echo "3. 命名空间:"
kubectl get namespace safety-event-system
echo ""

echo "4. 所有资源:"
kubectl get all -n safety-event-system
echo ""

echo "5. HPA 状态:"
kubectl get hpa -n safety-event-system
echo ""

echo "6. PVC 状态:"
kubectl get pvc -n safety-event-system
echo ""

echo "7. 服务外部 IP:"
kubectl get services -n safety-event-system
echo ""

echo "8. Pod 资源使用:"
kubectl top pods -n safety-event-system 2>/dev/null || echo "Metrics not ready yet"
echo ""

echo "=== 验证完成 ==="
```

## 清理资源

如果需要删除部署：

```bash
# 删除应用（保留集群）
kubectl delete namespace safety-event-system

# 删除整个集群
gcloud container clusters delete safety-event-cluster --region=us-central1
```

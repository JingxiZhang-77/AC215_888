#!/bin/bash

export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"

echo "========================================="
echo "Kubernetes 部署验证报告"
echo "========================================="
echo ""

echo "1. 集群节点状态："
kubectl get nodes --no-headers | wc -l | xargs echo "节点数量:"
echo ""

echo "2. Pod 状态："
kubectl get pods -n safety-event-system --no-headers 2>/dev/null | awk '{print $1 " - " $3}' || echo "无法获取 Pod 状态"
echo ""

echo "3. 服务外部 IP："
kubectl get services -n safety-event-system --no-headers 2>/dev/null | awk '{print $1 ": " $4}' || echo "无法获取服务状态"
echo ""

echo "4. HPA 状态："
kubectl get hpa -n safety-event-system --no-headers 2>/dev/null | awk '{print $1 " - 副本数: " $5}' || echo "无法获取 HPA 状态"
echo ""

API_IP="136.111.94.120"
FRONTEND_IP="34.136.237.225"

echo "5. API 访问测试："
echo "API URL: http://${API_IP}:9000"
timeout 3 curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://${API_IP}:9000/api/v1/health 2>/dev/null || echo "API 无响应"
echo ""

echo "6. Frontend 访问测试："
echo "Frontend URL: http://${FRONTEND_IP}"
timeout 3 curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://${FRONTEND_IP} 2>/dev/null || echo "Frontend 无响应"
echo ""

echo "========================================="
echo "验证完成"
echo "========================================="

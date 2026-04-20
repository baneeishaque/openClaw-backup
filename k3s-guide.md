# K3s 从入门到运维完整指南

> 轻量级 Kubernetes 发行版，专为边缘计算和资源受限环境设计

---

## 📋 前置准备

| 要求 | 说明 |
|------|------|
| 系统 | Linux（推荐 Ubuntu 20.04+/CentOS 7+） |
| 内存 | Server 2GB+，Agent 1GB+ |
| 网络 | 节点间 6443 端口互通 |
| 权限 | root 或 sudo |

---

## 一、单节点快速开始（练手）

### 1.1 一键安装

```bash
curl -sfL https://get.k3s.io | sh -
```

### 1.2 验证安装

```bash
# 查看节点状态
sudo kubectl get nodes

# 预期输出：
# NAME     STATUS   ROLES                  AGE
# ubuntu   Ready    control-plane,master   2m
```

### 1.3 跑个 Nginx 试试

```bash
# 创建 Deployment
sudo kubectl create deployment nginx --image=nginx

# 暴露服务
sudo kubectl expose deployment nginx --port=80 --type=NodePort

# 查看访问地址
sudo kubectl get svc nginx
# 访问：http://<你的IP>:<NodePort端口>
```

### 1.4 配置非 root 用户（可选）

```bash
# 添加当前用户到 k3s 组
sudo usermod -aG k3s $USER

# 配置 kubeconfig
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config
chmod 600 ~/.kube/config

# 添加到 ~/.bashrc
export KUBECONFIG=~/.kube/config
```

---

## 二、多节点集群部署

### 架构图

```
┌─────────────┐         ┌─────────────┐
│   Server    │◄────────│   Agent 1   │
│ (控制平面)   │         │  (工作节点)  │
│  - API Server│         └─────────────┘
│  - etcd     │◄────────┌─────────────┐
│  - Scheduler│         │   Agent 2   │
└─────────────┘         │  (工作节点)  │
                        └─────────────┘
```

### 2.1 Server 节点（主控）

```bash
# 安装并设置固定 Token（方便 Agent 加入）
curl -sfL https://get.k3s.io | sh -s - server --token my-secret-token

# 获取节点加入用的 Token（记下来！）
sudo cat /var/lib/rancher/k3s/server/node-token
# 输出类似：K10xxxxxxxxxxxxx::server:my-secret-token
```

### 2.2 Agent 节点（工作节点）

```bash
# 在每个 Agent 机器上执行
curl -sfL https://get.k3s.io | K3S_URL=https://<SERVER_IP>:6443 \
  K3S_TOKEN=my-secret-token sh -
```

### 2.3 验证集群

```bash
# 在 Server 上执行
sudo kubectl get nodes

# 预期输出：
NAME        STATUS   ROLES                  AGE
server      Ready    control-plane,master   10m
agent-1     Ready    <none>                 3m
agent-2     Ready    <none>                 3m
```

---

## 三、日常运维命令速查

### 3.1 查看状态

```bash
sudo kubectl get nodes                    # 查看所有节点
sudo kubectl get nodes -o wide            # 查看节点详情（含IP）
sudo kubectl get pods -A                  # 查看所有 Pod
sudo kubectl get pods -n <namespace>      # 查看指定命名空间
sudo kubectl get svc -A                   # 查看所有服务
sudo kubectl get all -A                   # 查看所有资源
```

### 3.2 部署应用

```bash
# YAML 方式（推荐生产使用）
sudo kubectl apply -f deployment.yaml

# 命令行快速创建
sudo kubectl create deployment web --image=nginx --replicas=3
sudo kubectl expose deployment web --port=80 --type=NodePort

# 扩缩容
sudo kubectl scale deployment web --replicas=5

# 删除部署
sudo kubectl delete deployment web
sudo kubectl delete svc web
```

### 3.3 排查问题

```bash
# 查看 Pod 详情（事件、状态）
sudo kubectl describe pod <pod-name>
sudo kubectl describe pod <pod-name> -n <namespace>

# 查看日志
sudo kubectl logs <pod-name>
sudo kubectl logs <pod-name> -f              # 实时跟踪
sudo kubectl logs <pod-name> --tail=100      # 最后100行
sudo kubectl logs <pod-name> -c <container>  # 多容器 Pod

# 进入容器调试
sudo kubectl exec -it <pod-name> -- /bin/sh
sudo kubectl exec -it <pod-name> -c <container> -- /bin/bash

# 查看节点详情
sudo kubectl describe node <node-name>
```

### 3.4 节点维护

```bash
# 标记节点不可调度（维护前）
sudo kubectl cordon <node-name>

# 驱逐节点上的 Pod（维护前）
sudo kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# 恢复节点调度
sudo kubectl uncordon <node-name>

# 删除节点（从集群移除）
sudo kubectl delete node <node-name>

# 然后在被删除的节点上执行卸载
sudo /usr/local/bin/k3s-agent-uninstall.sh
```

### 3.5 K3s 服务管理

```bash
# 查看 K3s 服务状态
sudo systemctl status k3s          # Server
sudo systemctl status k3s-agent    # Agent

# 启停服务
sudo systemctl start k3s
sudo systemctl stop k3s
sudo systemctl restart k3s

# 查看 K3s 日志
sudo journalctl -u k3s -f
```

---

## 四、YAML 部署示例

### 4.1 基础 Deployment + Service

```yaml
# web.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  labels:
    app: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  type: NodePort
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080
```

```bash
# 部署
sudo kubectl apply -f web.yaml

# 查看
sudo kubectl get pods -l app=web
sudo kubectl get svc web

# 访问：http://<任意节点IP>:30080
```

### 4.2 ConfigMap 配置

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database.properties: |
    db.host=mysql
    db.port=3306
  app.conf: |
    log_level=info
```

### 4.3 Secret 密钥

```bash
# 创建 Secret
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password='your-password'
```

---

## 五、高级配置

### 5.1 安装时自定义配置

```bash
# 禁用内置组件，使用 Docker
curl -sfL https://get.k3s.io | sh -s - server \
  --disable=traefik \
  --disable=servicelb \
  --docker

# 常用禁用选项：
# --disable=traefik      # 禁用默认 Ingress
# --disable=servicelb    # 禁用 ServiceLB
# --disable=metrics-server  # 禁用 Metrics Server
# --disable=coredns      # 禁用 CoreDNS
```

### 5.2 配置文件方式（/etc/rancher/k3s/config.yaml）

```yaml
# Server 配置
write-kubeconfig-mode: "0644"
tls-san:
  - "k3s.example.com"
  - "192.168.1.100"
disable:
  - traefik
  - servicelb
node-label:
  - "env=production"
```

### 5.3 高可用部署（3 Server + N Agent）

```bash
# ========== 第1个 Server ==========
curl -sfL https://get.k3s.io | sh -s - server \
  --cluster-init \
  --token my-secret-token

# ========== 第2、3个 Server 加入 ==========
curl -sfL https://get.k3s.io | sh -s - server \
  --server https://<SERVER_1_IP>:6443 \
  --token my-secret-token

# ========== Agent 加入（指向任意 Server）==========
curl -sfL https://get.k3s.io | K3S_URL=https://<SERVER_IP>:6443 \
  K3S_TOKEN=my-secret-token sh -
```

---

## 六、卸载

```bash
# Server 节点
sudo /usr/local/bin/k3s-uninstall.sh

# Agent 节点
sudo /usr/local/bin/k3s-agent-uninstall.sh
```

---

## 七、常见问题

### Q1: kubectl 命令报错 "The connection to the server was refused"

```bash
# 检查 K3s 服务
sudo systemctl status k3s

# 检查 kubeconfig
sudo cat /etc/rancher/k3s/k3s.yaml
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```

### Q2: 节点显示 NotReady

```bash
# 查看节点详情
sudo kubectl describe node <node-name>

# 检查 Agent 服务
sudo systemctl status k3s-agent
sudo journalctl -u k3s-agent -f
```

### Q3: Pod 一直 Pending

```bash
# 查看 Pod 事件
sudo kubectl describe pod <pod-name>

# 常见原因：
# - 资源不足（内存/CPU）
# - 镜像拉取失败
# - 节点不可调度
```

---

## 八、学习路线图

```
初学者
  │
  ▼
单节点部署 ──► 熟悉 kubectl 基础命令
  │
  ▼
多节点集群 ──► 应用部署、服务暴露
  │
  ▼
高可用架构 ──► 3 Server + N Agent
  │
  ▼
生产运维 ──► 监控、日志、备份、升级
```

---

## 参考资源

- 官方文档：https://docs.k3s.io/
- 中文文档：https://docs.rancher.cn/docs/k3s/latest/zh/
- GitHub：https://github.com/k3s-io/k3s

---

*文档生成时间：2026-03-20*

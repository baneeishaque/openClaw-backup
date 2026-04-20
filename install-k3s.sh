#!/bin/bash
#
# K3s 一键安装脚本
# 支持：单节点、Server、Agent、高可用
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
K3S_VERSION=""
K3S_TOKEN=""
K3S_SERVER_URL=""
NODE_NAME=""
INSTALL_MODE="single"  # single/server/agent
EXTRA_ARGS=""

# 打印信息
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# 检查系统
check_system() {
    info "检查系统环境..."
    
    # 检查是否为 Linux
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        error "本脚本仅支持 Linux 系统"
    fi
    
    # 检查 root 权限
    if [[ $EUID -ne 0 ]]; then
        warn "建议使用 root 权限运行，或使用 sudo"
    fi
    
    # 检查必要命令
    for cmd in curl systemctl; do
        if ! command -v $cmd &> /dev/null; then
            error "缺少必要命令: $cmd"
        fi
    done
    
    # 检查内存
    MEM_TOTAL=$(free -m | awk '/^Mem:/{print $2}')
    if [[ $MEM_TOTAL -lt 1024 ]]; then
        warn "内存不足 1GB，可能影响运行"
    fi
    
    success "系统检查通过"
}

# 显示帮助
show_help() {
    cat << EOF
K3s 一键安装脚本

用法: $0 [选项]

选项:
    -m, --mode <mode>       安装模式: single(单节点) | server(主控) | agent(工作节点) [默认: single]
    -t, --token <token>     集群 Token（server/agent 模式必需）
    -s, --server <url>      Server URL（agent 模式必需，如 https://192.168.1.100:6443）
    -n, --node-name <name>  节点名称（可选）
    -v, --version <ver>     指定 K3s 版本（可选，如 v1.28.5+k3s1）
    --disable <components>  禁用组件，逗号分隔（如 traefik,servicelb）
    --docker                使用 Docker 而非 containerd
    --flannel-backend <backend>  Flannel 后端（vxlan/host-gcc/wireguard）
    --tls-san <ips>         TLS SAN 额外 IP，逗号分隔
    --cluster-init          初始化高可用集群（第1个 server）
    --server-url <url>      高可用模式，加入已有 server
    -h, --help              显示帮助

示例:
    # 单节点安装
    $0

    # Server 节点（带固定 token）
    $0 -m server -t my-secret-token

    # Agent 节点加入集群
    $0 -m agent -t my-secret-token -s https://192.168.1.100:6443

    # 高可用第1个 Server
    $0 -m server -t my-secret-token --cluster-init

    # 高可用其他 Server 加入
    $0 -m server -t my-secret-token --server-url https://192.168.1.100:6443

    # 自定义配置
    $0 -m server -t my-token --disable traefik,servicelb --docker

EOF
}

# 解析参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -m|--mode)
                INSTALL_MODE="$2"
                shift 2
                ;;
            -t|--token)
                K3S_TOKEN="$2"
                shift 2
                ;;
            -s|--server)
                K3S_SERVER_URL="$2"
                shift 2
                ;;
            -n|--node-name)
                NODE_NAME="$2"
                shift 2
                ;;
            -v|--version)
                K3S_VERSION="$2"
                shift 2
                ;;
            --disable)
                IFS=',' read -ra COMPONENTS <<< "$2"
                for comp in "${COMPONENTS[@]}"; do
                    EXTRA_ARGS="$EXTRA_ARGS --disable=$comp"
                done
                shift 2
                ;;
            --docker)
                EXTRA_ARGS="$EXTRA_ARGS --docker"
                shift
                ;;
            --flannel-backend)
                EXTRA_ARGS="$EXTRA_ARGS --flannel-backend=$2"
                shift 2
                ;;
            --tls-san)
                IFS=',' read -ra IPS <<< "$2"
                for ip in "${IPS[@]}"; do
                    EXTRA_ARGS="$EXTRA_ARGS --tls-san=$ip"
                done
                shift 2
                ;;
            --cluster-init)
                EXTRA_ARGS="$EXTRA_ARGS --cluster-init"
                shift
                ;;
            --server-url)
                EXTRA_ARGS="$EXTRA_ARGS --server=https://$2:6443"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error "未知参数: $1"
                ;;
        esac
    done
}

# 验证参数
validate_args() {
    case $INSTALL_MODE in
        single)
            info "安装模式: 单节点"
            ;;
        server)
            info "安装模式: Server 节点"
            if [[ -z "$K3S_TOKEN" ]]; then
                warn "未指定 Token，将自动生成"
            fi
            ;;
        agent)
            info "安装模式: Agent 节点"
            if [[ -z "$K3S_TOKEN" ]]; then
                error "Agent 模式必须指定 --token"
            fi
            if [[ -z "$K3S_SERVER_URL" ]]; then
                error "Agent 模式必须指定 --server"
            fi
            ;;
        *)
            error "未知安装模式: $INSTALL_MODE"
            ;;
    esac
}

# 安装 K3s
install_k3s() {
    info "开始安装 K3s..."
    
    # 设置版本
    if [[ -n "$K3S_VERSION" ]]; then
        export INSTALL_K3S_VERSION="$K3S_VERSION"
        info "指定版本: $K3S_VERSION"
    fi
    
    case $INSTALL_MODE in
        single)
            info "执行单节点安装..."
            curl -sfL https://get.k3s.io | sh -s - server $EXTRA_ARGS
            ;;
        server)
            info "执行 Server 安装..."
            if [[ -n "$K3S_TOKEN" ]]; then
                export K3S_TOKEN="$K3S_TOKEN"
            fi
            curl -sfL https://get.k3s.io | sh -s - server $EXTRA_ARGS
            ;;
        agent)
            info "执行 Agent 安装..."
            export K3S_URL="$K3S_SERVER_URL"
            export K3S_TOKEN="$K3S_TOKEN"
            curl -sfL https://get.k3s.io | sh -s - agent $EXTRA_ARGS
            ;;
    esac
    
    success "K3s 安装完成"
}

# 配置环境
setup_env() {
    info "配置环境..."
    
    # 创建 kubeconfig 软链接
    if [[ ! -f ~/.kube/config && -f /etc/rancher/k3s/k3s.yaml ]]; then
        mkdir -p ~/.kube
        cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
        chmod 600 ~/.kube/config
        success "Kubeconfig 已配置到 ~/.kube/config"
    fi
    
    # 添加环境变量到 .bashrc
    if ! grep -q "KUBECONFIG" ~/.bashrc 2>/dev/null; then
        echo 'export KUBECONFIG=~/.kube/config' >> ~/.bashrc
        echo 'alias k=kubectl' >> ~/.bashrc
        info "已添加 KUBECONFIG 到 ~/.bashrc"
    fi
}

# 验证安装
verify_install() {
    info "验证安装..."
    
    # 等待服务启动
    sleep 3
    
    if [[ "$INSTALL_MODE" == "agent" ]]; then
        # Agent 只检查服务状态
        if systemctl is-active --quiet k3s-agent; then
            success "K3s Agent 运行正常"
        else
            error "K3s Agent 启动失败"
        fi
    else
        # Server 检查节点状态
        if command -v kubectl &> /dev/null; then
            NODE_STATUS=$(kubectl get nodes --no-headers 2>/dev/null | awk '{print $2}' | head -1)
            if [[ "$NODE_STATUS" == "Ready" ]]; then
                success "K3s Server 运行正常"
                echo ""
                info "节点状态:"
                kubectl get nodes
                echo ""
                info "系统 Pod 状态:"
                kubectl get pods -n kube-system
            else
                warn "节点状态: $NODE_STATUS，请检查日志"
            fi
        fi
    fi
}

# 显示后续步骤
show_next_steps() {
    echo ""
    echo "========================================"
    success "K3s 安装完成！"
    echo "========================================"
    echo ""
    
    case $INSTALL_MODE in
        single)
            echo "后续操作:"
            echo "  1. 查看节点: kubectl get nodes"
            echo "  2. 查看 Pod: kubectl get pods -A"
            echo "  3. 部署应用: kubectl create deployment nginx --image=nginx"
            echo ""
            echo "Token（用于添加 Agent）:"
            echo "  $(cat /var/lib/rancher/k3s/server/node-token 2>/dev/null || echo '请查看 /var/lib/rancher/k3s/server/node-token')"
            ;;
        server)
            echo "Server 节点信息:"
            echo "  - 地址: https://$(hostname -I | awk '{print $1}'):6443"
            echo "  - Token: $(cat /var/lib/rancher/k3s/server/node-token 2>/dev/null || echo $K3S_TOKEN)"
            echo ""
            echo "添加 Agent 命令:"
            echo "  curl -sfL https://get.k3s.io | K3S_URL=https://$(hostname -I | awk '{print $1}'):6443 K3S_TOKEN=$(cat /var/lib/rancher/k3s/server/node-token 2>/dev/null || echo $K3S_TOKEN) sh -"
            ;;
        agent)
            echo "Agent 节点已加入集群: $K3S_SERVER_URL"
            echo "在 Server 上执行 'kubectl get nodes' 查看"
            ;;
    esac
    
    echo ""
    echo "常用命令:"
    echo "  kubectl get nodes          # 查看节点"
    echo "  kubectl get pods -A        # 查看所有 Pod"
    echo "  kubectl get svc -A         # 查看所有服务"
    echo "  systemctl status k3s       # 查看服务状态"
    echo "  journalctl -u k3s -f       # 查看日志"
    echo ""
    echo "卸载命令:"
    if [[ "$INSTALL_MODE" == "agent" ]]; then
        echo "  /usr/local/bin/k3s-agent-uninstall.sh"
    else
        echo "  /usr/local/bin/k3s-uninstall.sh"
    fi
}

# 主函数
main() {
    echo "========================================"
    echo "       K3s 一键安装脚本"
    echo "========================================"
    echo ""
    
    parse_args "$@"
    validate_args
    check_system
    install_k3s
    setup_env
    verify_install
    show_next_steps
}

# 执行
main "$@"

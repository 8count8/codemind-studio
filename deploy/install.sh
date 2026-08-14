#!/bin/bash
# ============================================================
# CodeMind Studio - 阿里云云服务器一键部署脚本
# 适用系统: Ubuntu 22.04 LTS
# 用法: sudo bash deploy.sh
# ============================================================

set -e

# ===== 颜色输出 =====
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_banner() {
    echo -e "${GREEN}"
    echo "================================================"
    echo "   CodeMind Studio - 一键部署脚本"
    echo "   部署到: 阿里云云服务器"
    echo "   数据库: MySQL"
    echo "================================================"
    echo -e "${NC}"
}

print_step() {
    echo -e "${YELLOW}[STEP] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[OK] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# ===== 检查 root 权限 =====
if [ "$EUID" -ne 0 ]; then
    print_error "请使用 sudo 运行此脚本: sudo bash deploy.sh"
    exit 1
fi

# ===== 项目配置 =====
PROJECT_DIR="/opt/codemind"
APP_USER="codemind"
APP_PORT=8000
DB_NAME="codemind"
DB_USER="codemind"

print_banner

# ============================================================
# Step 1: 更新系统 & 安装基础依赖
# ============================================================
print_step "Step 1: 更新系统并安装基础依赖..."

apt update -y
apt upgrade -y

apt install -y \
    python3 python3-pip python3-venv \
    nginx mysql-server \
    git curl wget \
    build-essential

print_success "基础依赖安装完成"

# ============================================================
# Step 2: 创建应用用户
# ============================================================
print_step "Step 2: 创建应用用户和目录..."

if ! id "$APP_USER" &>/dev/null; then
    useradd -r -s /bin/bash "$APP_USER"
    print_success "创建用户: $APP_USER"
fi

mkdir -p "$PROJECT_DIR"
mkdir -p /var/log/codemind

print_success "目录创建完成"

# ============================================================
# Step 3: 配置 MySQL
# ============================================================
print_step "Step 3: 配置 MySQL 数据库..."

# 启动 MySQL 服务
systemctl start mysql
systemctl enable mysql

# 设置 MySQL root 密码（如果还没设置）
MYSQL_ROOT_PASS=$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9' | head -c 16)

# 创建数据库和用户
mysql -u root << EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY 'codemind_db_pass_2024';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF

print_success "MySQL 配置完成"
echo "  数据库名: $DB_NAME"
echo "  数据库用户: $DB_USER"
echo "  数据库密码: codemind_db_pass_2024"

# ============================================================
# Step 4: 克隆/部署代码
# ============================================================
print_step "Step 4: 部署应用代码..."

# 如果项目目录为空，从 git 克隆
if [ -z "$(ls -A "$PROJECT_DIR" 2>/dev/null)" ]; then
    print_step "克隆代码到 $PROJECT_DIR..."
    cd /tmp
    git clone https://github.com/8count8/codemind-studio.git "$PROJECT_DIR" 2>/dev/null || {
        # 如果没有 GitHub 访问权限，使用本地文件
        print_yellow "无法从 GitHub 克隆，请手动将项目文件放到 $PROJECT_DIR"
        print_yellow "然后重新运行此脚本"
        exit 1
    }
fi

cd "$PROJECT_DIR"

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装 Python 依赖
pip install --upgrade pip
pip install -r requirements.txt

print_success "Python 依赖安装完成"

# ============================================================
# Step 5: 创建环境配置
# ============================================================
print_step "Step 5: 创建环境配置文件..."

# 获取服务器公网 IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

# 检查是否有 .env 文件
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cat > "$PROJECT_DIR/.env" << EOF
# ===== 应用配置 =====
FLASK_ENV=production
SECRET_KEY=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)

# ===== MySQL 数据库配置 =====
DB_HOST=localhost
DB_PORT=3306
DB_USER=${DB_USER}
DB_PASSWORD=codemind_db_pass_2024
DB_NAME=${DB_NAME}

# ===== 邮件服务配置 =====
EMAIL_TYPE=NETEASE_EMAIL_SMTP_SSL
EMAIL_ADDRESS=cms202504@163.com
# 请在部署后修改为你的网易邮箱授权码
EMAIL_PASSWORD=your-email-auth-code

# ===== CORS 配置 =====
CORS_ORIGINS=http://${SERVER_IP}

# ===== 服务器配置 =====
SERVER_IP=${SERVER_IP}
EOF
    
    print_success "创建默认 .env 配置文件"
    print_yellow "重要: 请修改 $PROJECT_DIR/.env 中的 EMAIL_PASSWORD 为你的网易邮箱授权码"
else
    print_success ".env 配置文件已存在，跳过创建"
fi

chown -R "$APP_USER:$APP_USER" "$PROJECT_DIR"
chown -R "$APP_USER:$APP_USER" /var/log/codemind

print_success "环境配置完成"

# ============================================================
# Step 6: 配置 Gunicorn systemd 服务
# ============================================================
print_step "Step 6: 配置 Gunicorn 服务..."

cat > /etc/systemd/system/codemind.service << 'SERVICE_EOF'
[Unit]
Description=CodeMind Studio - Flask Backend
After=network.target mysql.service

[Service]
Type=simple
User=codemind
Group=codemind
WorkingDirectory=/opt/codemind
EnvironmentFile=/opt/codemind/.env
ExecStart=/opt/codemind/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile /var/log/codemind/access.log \
    --error-logfile /var/log/codemind/error.log \
    run:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE_EOF

systemctl daemon-reload
systemctl start codemind
systemctl enable codemind

print_success "Gunicorn 服务配置完成"

# ============================================================
# Step 7: 配置 Nginx
# ============================================================
print_step "Step 7: 配置 Nginx..."

# 创建 Nginx 配置
cat > /etc/nginx/sites-available/codemind << 'NGINX_EOF'
server {
    listen 80 default_server;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120;
    }
}
NGINX_EOF

# 禁用默认站点
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
fi

# 启用新站点
ln -sf /etc/nginx/sites-available/codemind /etc/nginx/sites-enabled/codemind

# 测试 Nginx 配置
nginx -t

# 重启 Nginx
systemctl restart nginx

# 设置防火墙
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

print_success "Nginx 配置完成"

# ============================================================
# Step 8: 验证部署
# ============================================================
print_step "Step 8: 验证部署..."

sleep 2

# 检查 Gunicorn 服务状态
if systemctl is-active --quiet codemind; then
    print_success "Gunicorn 服务运行中"
else
    print_error "Gunicorn 服务未运行，请检查日志: journalctl -u codemind"
fi

# 检查 Nginx 服务状态
if systemctl is-active --quiet nginx; then
    print_success "Nginx 服务运行中"
else
    print_error "Nginx 服务未运行"
fi

# 测试健康检查接口
HEALTH_CHECK=$(curl -s http://127.0.0.1:8000/health 2>/dev/null)
if echo "$HEALTH_CHECK" | grep -q '"status": "ok"'; then
    print_success "健康检查接口正常"
else
    print_yellow "健康检查接口可能需要更多时间启动"
fi

# ============================================================
# 完成
# ============================================================
echo ""
echo -e "${GREEN}================================================"
echo "   部署完成!"
echo "================================================"
echo -e "${NC}"
echo "服务器 IP: ${SERVER_IP}"
echo "访问地址: http://${SERVER_IP}"
echo ""
echo "常用命令:"
echo "  查看服务状态: systemctl status codemind"
echo "  重启服务: systemctl restart codemind"
echo "  查看日志: tail -f /var/log/codemind/error.log"
echo "  Nginx 配置: /etc/nginx/sites-available/codemind"
echo ""
echo -e "${YELLOW}重要提醒:${NC}"
echo "  1. 修改 /opt/codemind/.env 中的 EMAIL_PASSWORD"
echo "  2. 在阿里云控制台开放 80 端口防火墙"
echo "  3. 如需 HTTPS，配置 SSL 证书后修改 Nginx 配置"
echo ""

# PyDDNS

自动更新Cloudflare DNS记录的IPv6动态DNS更新工具。

## 安装

```bash
# 1. 克隆仓库
git clone git@github.com:itsaquestion/pyddns.git
cd pyddns

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑.env文件，填入你的配置
```

## 配置说明

`.env` 文件配置：
```
CF_API_TOKEN=your_cloudflare_api_token
DOMAIN=example.com
RECORD_NAME=home.example.com
CHECK_INTERVAL=5
```

## 作为服务运行

```bash
# 1. 安装服务
sudo cp pyddns.service /etc/systemd/system/

# 2. 启动服务
sudo systemctl daemon-reload
sudo systemctl enable pyddns
sudo systemctl start pyddns

# 3. 查看状态
sudo systemctl status pyddns
```

## 日志

查看服务日志：
```bash
sudo journalctl -u pyddns -f
```
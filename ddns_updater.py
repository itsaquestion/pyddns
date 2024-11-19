import os
import time
import requests
import schedule
from dotenv import load_dotenv
import logging
import socket
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ddns.log')
    ]
)

# 加载环境变量
load_dotenv()

# 配置
CF_API_TOKEN = os.getenv('CF_API_TOKEN')
DOMAIN = os.getenv('DOMAIN')
RECORD_NAME = os.getenv('RECORD_NAME')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '5'))

def get_local_ipv6():
    """获取本地IPv6地址"""
    try:
        # 创建一个IPv6套接字
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        # 连接到一个IPv6地址（这里不会真正建立连接）
        sock.connect(("2001:4860:4860::8888", 80))
        # 获取本地IPv6地址
        local_ip = sock.getsockname()[0]
        sock.close()
        return local_ip
    except Exception as e:
        logging.error(f"获取本地IPv6地址失败: {str(e)}")
        return None

def get_cloudflare_zone_id():
    """获取Cloudflare域名的Zone ID"""
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(
        "https://api.cloudflare.com/client/v4/zones",
        headers=headers
    )
    
    if response.status_code == 200:
        for zone in response.json()['result']:
            if zone['name'] == DOMAIN:
                return zone['id']
    return None

def get_dns_record(zone_id):
    """获取DNS记录"""
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(
        f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
        headers=headers
    )
    
    if response.status_code == 200:
        for record in response.json()['result']:
            if record['name'] == RECORD_NAME and record['type'] == 'AAAA':
                return record
    return None

def update_dns_record(zone_id, record_id, ipv6_address):
    """更新DNS记录"""
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "type": "AAAA",
        "name": RECORD_NAME,
        "content": ipv6_address,
        "proxied": False
    }
    
    response = requests.put(
        f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}",
        headers=headers,
        json=data
    )
    
    return response.status_code == 200

def check_and_update():
    """检查并更新DNS记录"""
    try:
        # 获取本地IPv6地址
        local_ipv6 = get_local_ipv6()
        if not local_ipv6:
            logging.error("无法获取本地IPv6地址")
            return

        # 获取Zone ID
        zone_id = get_cloudflare_zone_id()
        if not zone_id:
            logging.error("无法获取Zone ID")
            return

        # 获取当前DNS记录
        dns_record = get_dns_record(zone_id)
        if not dns_record:
            logging.error("无法获取DNS记录")
            return

        current_ip = dns_record['content']
        
        # 比较IP地址
        if current_ip != local_ipv6:
            logging.info(f"检测到IP变化: {current_ip} -> {local_ipv6}")
            if update_dns_record(zone_id, dns_record['id'], local_ipv6):
                logging.info("DNS记录更新成功")
            else:
                logging.error("DNS记录更新失败")
        else:
            logging.info("IP地址未发生变化，无需更新")
            
    except Exception as e:
        logging.error(f"更新过程中发生错误: {str(e)}")

def main():
    """主函数"""
    if not all([CF_API_TOKEN, DOMAIN, RECORD_NAME]):
        logging.error("请检查环境变量配置")
        return

    logging.info("DDNS更新服务启动")
    logging.info(f"域名: {RECORD_NAME}")
    logging.info(f"检查间隔: {CHECK_INTERVAL}分钟")

    # 立即执行一次
    check_and_update()
    
    # 设置定时任务
    schedule.every(CHECK_INTERVAL).minutes.do(check_and_update)
    
    # 保持程序运行
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()

import uuid
import requests
import time
import toml

RESTART_DELAY = 2  # 重启延迟时间（秒）

def run_client():
    # 生成 UUID
    client_uuid = str(uuid.uuid4())

    try:
        # 注册请求
        response = requests.post('http://39.106.56.202:20010/register', json={'uuid': client_uuid})
        if response.status_code == 200:
            data = response.json()
            gateway_port = data['gateway_port']
            ssh_port = data['ssh_port']
            print(f"Assigned gateway port: {gateway_port}, ssh port: {ssh_port}")

            # 修改 frpc.toml 文件
            with open('/config/frpc.toml', 'r') as f:
                config = toml.load(f)

            for proxy in config['proxies']:
                if proxy['name'] == 'hit-star-gateway':
                    proxy['name'] = f'hit-star-gateway-{client_uuid}'
                    proxy['remotePort'] = gateway_port
                elif proxy['name'] == 'hit-star-ssh':
                    proxy['name'] = f'hit-star-ssh-{client_uuid}'
                    proxy['remotePort'] = ssh_port

            with open('/config/frpc.toml', 'w') as f:
                toml.dump(config, f)

            # 发送心跳包
            while True:
                try:
                    requests.post('http://39.106.56.202:20010/heartbeat', json={'uuid': client_uuid})
                except requests.RequestException as e:
                    print(f"Heartbeat error: {e}")
                    raise  # 重新抛出异常以触发重启
                time.sleep(1)
        else:
            print(f"Registration failed: {response.text}")
            raise requests.RequestException("Registration failed")
    except requests.RequestException as e:
        print(f"Connection error: {e}")
        raise  # 重新抛出异常以触发重启


while True:
    try:
        run_client()
    except Exception as e:
        print(f"Client encountered an error: {e}. Restarting in {RESTART_DELAY} seconds...")
        time.sleep(RESTART_DELAY)
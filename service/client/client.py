import requests
import uuid
import toml
import os
import time
from pathlib import Path

class FrpcConfigurator:
    def __init__(self, uuid):
        self.uuid = uuid
        self.config_path = Path("/config/frpc.toml")
        
    def modify_config(self, gateway_port, ssh_port):
        config = toml.load(self.config_path)
        
        for proxy in config['proxy']:
            if proxy['name'] == 'hit-star-gateway':
                proxy['name'] = f"hit-star-gateway-{self.uuid}"
                proxy['remotePort'] = gateway_port
            elif proxy['name'] == 'hit-star-ssh':
                proxy['name'] = f"hit-star-ssh-{self.uuid}"
                proxy['remotePort'] = ssh_port
        
        with open(self.config_path, 'w') as f:
            toml.dump(config, f)

class Client:
    def __init__(self):
        self.uuid = str(uuid.uuid4())
        self.server_url = "http://39.106.56.202:20010"
        
    def start(self):
        # 注册客户端
        response = requests.post(f"{self.server_url}/register", json={'uuid': self.uuid})
        if response.status_code != 200:
            raise Exception("Registration failed")
        
        ports = response.json()
        # 修改配置文件
        configurator = FrpcConfigurator(self.uuid)
        configurator.modify_config(ports['gateway'], ports['ssh'])
        
        # 启动心跳
        while True:
            try:
                requests.post(f"{self.server_url}/heartbeat", json={'uuid': self.uuid})
                time.sleep(1)
            except Exception as e:
                print(f"Heartbeat error: {str(e)}")
                time.sleep(5)

if __name__ == '__main__':
    client = Client()
    while True:
        try:
            client.start()
        except Exception as e:
            print("Registration failed , Retry in 2 seconds.")
            sleep(2)

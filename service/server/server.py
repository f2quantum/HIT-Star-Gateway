from flask import Flask, render_template, request, jsonify
import sqlite3
import time
from threading import Lock
from collections import deque

app = Flask(__name__)
lock = Lock()

# 初始化端口池
gateway_ports = deque(range(30000, 35000))
ssh_ports = deque(range(35001, 40000))

# 数据库初始化
def init_db():
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clients
                 (uuid TEXT PRIMARY KEY,
                  gateway_port INTEGER,
                  ssh_port INTEGER,
                  last_heartbeat REAL,
                  status TEXT)''')
    conn.commit()
    conn.close()

# 端口回收线程
def port_reclaimer():
    while True:
        time.sleep(10)
        with lock:
            conn = sqlite3.connect('clients.db')
            c = conn.cursor()
            c.execute("SELECT uuid, last_heartbeat FROM clients")
            clients = c.fetchall()
            current_time = time.time()
            
            for client in clients:
                if current_time - client > 10:
                    # 回收端口
                    c.execute("SELECT gateway_port, ssh_port FROM clients WHERE uuid=?", (client,))
                    ports = c.fetchone()
                    gateway_ports.append(ports)
                    ssh_ports.append(ports)
                    
                    # 更新状态
                    c.execute("UPDATE clients SET status='offline' WHERE uuid=?", (client,))
                    conn.commit()
            conn.close()

# Flask路由
@app.route('/register', methods=['POST'])
def register():
    uuid = request.json.get('uuid')
    with lock:
        if not gateway_ports or not ssh_ports:
            return jsonify({"error": "No available ports"}), 500
            
        gateway = gateway_ports.popleft()
        ssh = ssh_ports.popleft()
        
        conn = sqlite3.connect('clients.db')
        c = conn.cursor()
        c.execute("INSERT INTO clients VALUES (?,?,?,?,?)",
                 (uuid, gateway, ssh, time.time(), 'online'))
        conn.commit()
        conn.close()
        
    return jsonify({"gateway": gateway, "ssh": ssh})

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    uuid = request.json.get('uuid')
    with lock:
        conn = sqlite3.connect('clients.db')
        c = conn.cursor()
        c.execute("UPDATE clients SET last_heartbeat=?, status='online' WHERE uuid=?",
                 (time.time(), uuid))
        conn.commit()
        conn.close()
    return jsonify({"status": "updated"})

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute("SELECT * FROM clients")
    data = c.fetchall()
    conn.close()
    return render_template('./templates/dashboard.html', clients=data)

# 新增服务启动初始化模块
def load_allocated_ports():
    """从数据库加载已分配端口"""
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute("SELECT gateway_port, ssh_port FROM clients WHERE status='online'")
    allocated = c.fetchall()
    conn.close()
    
    # 过滤已分配端口
    allocated_ports = set()
    for ports in allocated:
        allocated_ports.add(ports[0])
        allocated_ports.add(ports[1])

    # 重新生成可用端口池
    global gateway_ports, ssh_ports
    gateway_ports = deque([p for p in range(30000, 35001) if p not in allocated_ports])
    ssh_ports = deque([p for p in range(35001, 40000) if p not in allocated_ports])


if __name__ == '__main__':
    init_db()
    load_allocated_ports()
    import threading
    threading.Thread(target=port_reclaimer, daemon=True).start()
    app.run(host='0.0.0.0', port=20010)

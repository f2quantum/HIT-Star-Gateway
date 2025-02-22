import sqlite3
from flask import Flask, jsonify, render_template
from flask_restful import Api, Resource, reqparse
import threading
import time
from datetime import datetime

# 初始化Flask应用
app = Flask(__name__)
api = Api(app)

# 定义自定义过滤器：将时间戳转换为 datetime 对象
@app.template_filter('timestamp_to_datetime')
def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp)

# 定义自定义过滤器：strftime 用于格式化日期时间
@app.template_filter('strftime')
def strftime_filter(dt, format_str):
    return dt.strftime(format_str)

# 数据库初始化
conn = sqlite3.connect('clients.db')
c = conn.cursor()
# 创建表时直接包含 last_seen 列
c.execute('''CREATE TABLE IF NOT EXISTS clients
             (uuid TEXT PRIMARY KEY, gateway_port INTEGER, ssh_port INTEGER, last_seen REAL)''')
conn.commit()

# 端口集合
gateway_ports = list(range(30000, 35001))
ssh_ports = list(range(35001, 40000))

# 从数据库中读取已占用的端口
c.execute("SELECT gateway_port, ssh_port FROM clients")
occupied_ports = c.fetchall()
for gateway_port, ssh_port in occupied_ports:
    if gateway_port in gateway_ports:
        gateway_ports.remove(gateway_port)
    if ssh_port in ssh_ports:
        ssh_ports.remove(ssh_port)

# 解析器
parser = reqparse.RequestParser()
parser.add_argument('uuid', type=str, required=True, help='UUID is required')

# 检查客户端是否失活的线程
def check_inactivity():
    while True:
        current_time = time.time()
        conn = sqlite3.connect('clients.db')
        c = conn.cursor()
        c.execute("SELECT uuid, gateway_port, ssh_port FROM clients WHERE last_seen < ?", (current_time - 10,))
        inactive_clients = c.fetchall()
        for uuid, gateway_port, ssh_port in inactive_clients:
            gateway_ports.append(gateway_port)
            ssh_ports.append(ssh_port)
            c.execute("DELETE FROM clients WHERE uuid =?", (uuid,))
        conn.commit()
        conn.close()
        # 修改为每 10 秒检测一次
        time.sleep(10)

# 注册资源
class Register(Resource):
    def post(self):
        args = parser.parse_args()
        uuid = args['uuid']
        if not gateway_ports or not ssh_ports:
            return {'message': 'No available ports'}, 500
        gateway_port = gateway_ports.pop(0)
        ssh_port = ssh_ports.pop(0)
        current_time = time.time()
        conn = sqlite3.connect('clients.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO clients VALUES (?,?,?,?)", (uuid, gateway_port, ssh_port, current_time))
            conn.commit()
        except sqlite3.IntegrityError:
            return {'message': 'UUID already exists'}, 400
        conn.close()
        return {'gateway_port': gateway_port, 'ssh_port': ssh_port}, 200

# 心跳资源
class Heartbeat(Resource):
    def post(self):
        args = parser.parse_args()
        uuid = args['uuid']
        current_time = time.time()
        conn = sqlite3.connect('clients.db')
        c = conn.cursor()
        c.execute("UPDATE clients SET last_seen =? WHERE uuid =?", (current_time, uuid))
        rows_affected = conn.total_changes
        conn.commit()
        conn.close()
        if rows_affected == 0:
            return {'message': 'Client not found'}, 404
        return {'message': 'Heartbeat received'}, 200

# Web界面
@app.route('/')
def index():
    conn = sqlite3.connect('clients.db')
    c = conn.cursor()
    c.execute("SELECT uuid, gateway_port, ssh_port, last_seen FROM clients")
    clients = c.fetchall()
    current_time = time.time()
    active_clients = []
    for uuid, gateway_port, ssh_port, last_seen in clients:
        status = 'Online' if current_time - last_seen < 10 else 'Offline'
        active_clients.append({
            'uuid': uuid,
            'gateway_port': gateway_port,
            'ssh_port': ssh_port,
            'last_seen': last_seen,
            'status': status
        })
    conn.close()
    return render_template('index.html', clients=active_clients)

# 添加资源
api.add_resource(Register, '/register')
api.add_resource(Heartbeat, '/heartbeat')

if __name__ == '__main__':
    # 启动检查失活线程
    inactivity_thread = threading.Thread(target=check_inactivity)
    inactivity_thread.daemon = True
    inactivity_thread.start()
    app.run(host='0.0.0.0', port=20010)
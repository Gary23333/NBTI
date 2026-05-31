#!/usr/bin/env python3
"""NBTI 前端静态文件服务器 - 只提供 HTML/CSS/JS，代理 API 请求到后端"""

import os
import sys
import requests
from flask import Flask, send_from_directory, send_file, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 静态文件目录
STATIC_DIR = os.path.dirname(os.path.abspath(__file__))

# 后端 API 地址
BACKEND_URL = 'http://127.0.0.1:8081'

# 允许的文件类型
ALLOWED_EXTENSIONS = {'.html', '.css', '.js', '.svg', '.png', '.jpg', '.ico', '.json'}

@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_api(path):
    """代理所有 /api/* 请求到后端"""
    url = f'{BACKEND_URL}/api/{path}'
    
    # 转发请求头
    headers = {key: value for key, value in request.headers if key.lower() != 'host'}
    
    # 转发请求体
    data = request.get_data()
    
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=data,
            params=request.args,
            timeout=120,
            stream=True
        )
        
        # 构建响应
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        # 流式响应
        if 'text/event-stream' in resp.headers.get('content-type', ''):
            def generate():
                for chunk in resp.iter_content(chunk_size=None):
                    yield chunk
            return Response(generate(), resp.status_code, headers)
        
        return Response(resp.content, resp.status_code, headers)
    except requests.exceptions.RequestException as e:
        return {'error': f'Backend API error: {str(e)}'}, 502

@app.route('/<path:filename>')
def serve_file(filename):
    # 安全检查：只允许访问特定类型的文件
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return "Not Found", 404
    
    # 安全检查：防止路径遍历
    if '..' in filename or filename.startswith('/'):
        return "Forbidden", 403
    
    file_path = os.path.join(STATIC_DIR, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path)
    return "Not Found", 404

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    
    # 获取 IPv6 地址
    import socket
    ipv6_addr = None
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s.connect(("2001:4860:4860::8888", 80))
        ipv6_addr = s.getsockname()[0]
        s.close()
    except:
        pass
    
    print(f"🚀 NBTI 前端服务启动")
    print(f"📡 本机访问: http://localhost:{port}")
    if ipv6_addr:
        print(f"📡 公网 IPv6: http://[{ipv6_addr}]:{port}")
    print(f"📁 静态文件目录: {STATIC_DIR}")
    print(f"🔄 API 代理: {BACKEND_URL}")
    print(f"⚠️  注意: 此服务只提供静态文件 + API 代理，不包含 API 密钥")
    print(f"⚠️  后端 API 请运行: python server.py")
    
    app.run(host='::', port=port, debug=False, threaded=True)

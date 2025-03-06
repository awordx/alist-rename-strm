# import subprocess
# from flask import Flask, jsonify, request
#
# app = Flask(__name__)
# import requests
# #这个函数的作用是可以在网页上更新emby
# @app.route('/')
# def home():
#     return "Welcome to the Flask app!"
# @app.route('/emby_to_refresh')
# def run_script():
#     # 运行脚本并捕获输出
#     path = request.args.get('path')
#
#     # 如果没有传递路径参数，返回错误信息
#     if not path:
#         command = ['python3', '/volume1/docker/alist_rename/alist_rename.py']
#     else:
#         # 构建命令
#         command = [['python3', '/volume1/docker/alist_rename/alist_rename.py'], '--path', path]
#
#     # 运行脚本并捕获输出
#     result = subprocess.run(
#         command,
#         capture_output=True,
#         text=True  # 将输出作为字符串而不是字节
#     )
#     # 获取脚本的标准输出和错误输出
#     output = result.stdout.strip()  # 去掉多余空格
#     error = result.stderr.strip()  # 同样处理错误输出
#
#     with open('alist_rename_log.txt', 'w') as f:
#         f.write("Output:\n")
#         f.write(output + "\n")
#         f.write("Error:\n")
#         f.write(error)
#     # 返回输出结果
#     return jsonify(output,error)
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5060)


#
# # 首页路由
# @app.route('/')
# def index():
#     return render_template(r'index.html')
# def generate_output():
#     while True:
#         time.sleep(1)  # 模拟每秒钟输出一条消息
#         message = 'Output message'  # 实际情况中，可以在这里写入Python输出的逻辑
#         yield f"data: {message}\n\n"
#
# @app.route('/stream')
# def stream():
#     return Response(generate_output(), mimetype='text/event-stream')

# if __name__ == '__main__':
#     app.run()
# 运行脚本的路由（支持传递路径参数）

import subprocess
from flask import Flask, jsonify, request, render_template, Response
from alist_rename import read_config
app = Flask(__name__)

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')  # 确保这个文件在templates文件夹中

# SSE路由，用于实时输出
@app.route('/stream')
def stream():
    config = read_config('config/config.ini')
    scripts_path = config['user_config']['scripts_path']
    def generate(tvpath=None, moviepath=None):
        command = ['python3', scripts_path]

        # 根据请求参数构建命令
        if tvpath:
            command.append('--tvpath')
            command.append(tvpath)  # 使用传入的 tvpath
        if moviepath:
            command.append('--moviepath')
            command.append(moviepath)  # 使用传入的 moviepath

        # 打开日志文件以写入
        with open('data/alist_rename_log.txt', 'a') as log_file:
            # 记录执行的命令
            log_file.write(f"执行命令: {' '.join(command)}\n")
            log_file.flush()  # 刷新写入

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # 打开日志文件以写入
        with open('data/alist_rename_log.txt', 'a') as log_file:
            while True:
                output = process.stdout.readline()
                if output:
                    log_file.write(output)  # 将输出写入日志文件
                    log_file.flush()  # 刷新写入
                    yield f"{output.strip()}\n\n"
                if process.poll() is not None:
                    break

            # 如果有错误输出，也要返回
            stderr_output = process.stderr.read()
            if stderr_output:
                log_file.write(stderr_output)  # 将错误输出写入日志文件
                log_file.flush()  # 刷新写入
                yield f"{stderr_output.strip()}\n\n"

    # 从请求中获取 tvpath 和 moviepath 参数
    tvpath = request.args.get('tvpath')  # 获取 tvpath 参数
    moviepath = request.args.get('moviepath')  # 获取 moviepath 参数
    return Response(generate(tvpath, moviepath), content_type='text/event-stream; charset=utf-8')

# 启动Flask应用
if __name__ == '__main__':
    config = read_config('config/config.ini')
    port = config['user_config']['flask_port']
    app.run(host='0.0.0.0', port=port)
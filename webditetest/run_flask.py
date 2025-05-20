from flask import Flask, jsonify, request, render_template, Response
import time
import subprocess
from flask import Flask, jsonify, request, render_template, Response
import time
import subprocess
import threading
app = Flask(__name__)
import sys
import chardet
# 设置标准输出的编码为 UTF-8
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# 首页路由
@app.route('/')
def index():
    return render_template('index_new.html')  # 确保这个文件在templates文件夹中

@app.route('/hello', methods=['POST'])
def hello():
    return jsonify(message="Hello, World!")  # 返回 JSON 响应

log_buffer = []  # 用于存储日志的缓冲区

def generate_logs():
    while True:
        if log_buffer:
            log_line = log_buffer.pop(0)  # 从缓冲区获取日志
            yield f"data: {log_line}\n\n"
        time.sleep(0.5)

@app.route('/log_stream')
def log_stream():
    return Response(generate_logs(), mimetype='text/event-stream')

@app.route('/refresh', methods=['GET','POST'])
def run_script2():
    global log_buffer
    print("刷新已启动")


    def execute_command():
        print("正在执行脚本...")
        process = subprocess.Popen(
            ['python', r'/mnt/d/1FreeMove/alist_rename-strm-emby/alist_rename.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',  # 或尝试 'gbk'、'latin1'
            errors='replace'  # 替换无法解码的字符
        )

        for line in process.stdout:
            log_buffer.append(line.strip())  # 添加日志到缓冲区
            print(f"输出: {line.strip()}")  # 打印调试信息

        # 读取 stderr 输出的字节数据
        stderr_output = process.stderr.read()

        if stderr_output:
            print(f"错误输出: {stderr_output}")  # 打印错误信息

    # 启动线程
    threading.Thread(target=execute_command, daemon=True).start()
    print("线程已启动")

    return "刷新已启动"

@app.route('/stream')
def stream():
    # config = read_config('config/config.ini')
    # scripts_path = config['user_config']['scripts_path']
    def generate(tvpath=None, moviepath=None):
        command = ['python3', r'/mnt/d/1FreeMove/alist_rename-strm-emby/alist_rename.py']

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
    app.run(host='0.0.0.0', port=5000, debug=True)

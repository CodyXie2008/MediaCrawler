import subprocess
import webbrowser
import time
import sys
import os

def run_backend():
    # 启动后端 FastAPI
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        cwd="backend"
    )

def run_frontend():
    # 启动前端 Vite
    if os.name == "nt":
        # Windows
        return subprocess.Popen(["npm", "run", "dev"], cwd="frontend", shell=True)
    else:
        # macOS/Linux
        return subprocess.Popen(["npm", "run", "dev"], cwd="frontend")

if __name__ == "__main__":
    backend_proc = run_backend()
    time.sleep(3)  # 等待后端启动
    frontend_proc = run_frontend()
    time.sleep(5)  # 等待前端启动
    webbrowser.open("http://localhost:5173")
    print("MediaCrawler 可视化爬虫已启动，浏览器已自动打开。")
    print("按 Ctrl+C 可关闭所有服务。")
    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        backend_proc.terminate()
        frontend_proc.terminate()
        print("已关闭所有服务。") 
import subprocess
import threading

crawler_process = None
crawler_logs = []

def start_crawler(params):
    global crawler_process
    if crawler_process is not None:
        return {"status": "already running"}
    cmd = ["python", "main.py"]
    for k, v in params.items():
        if v is not None:
            cmd += [f"--{k}", str(v)]
    crawler_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    threading.Thread(target=_read_logs, daemon=True).start()
    return {"status": "started"}

def _read_logs():
    global crawler_process, crawler_logs
    for line in crawler_process.stdout:
        crawler_logs.append(line)
        if len(crawler_logs) > 1000:
            crawler_logs = crawler_logs[-1000:]

def stop_crawler():
    global crawler_process
    if crawler_process:
        crawler_process.terminate()
        crawler_process = None
    return {"status": "stopped"}

def get_status():
    return {"running": crawler_process is not None}

def get_logs():
    return {"logs": crawler_logs[-100:]} 
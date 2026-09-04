import sys
import os
import json
import webbrowser
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# Ensure UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from main import run_pipeline

app = Flask(__name__)
CACHE_FILE = "data/cache/latest_analysis.json"
cached_result = None

def load_cached_analysis():
    global cached_result
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached_result = json.load(f)
                return cached_result
        except Exception:
            pass
    return None

def save_analysis(data):
    global cached_result
    cached_result = data
    os.makedirs("data/cache", exist_ok=True)
    try:
        # Filter out non-serializable elements
        serializable = {
            "gate0": data.get("gate0", {}),
            "gate1": data.get("gate1", {}),
            "short_term_picks": data.get("short_term_picks", []),
            "long_term_picks": data.get("long_term_picks", []),
            "timestamp": data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        }
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error caching analysis: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def get_status():
    global cached_result
    if not cached_result:
        cached_result = load_cached_analysis()

    if not cached_result:
        # Run a quick initial run if no cache exists
        res = run_pipeline(sample_size=4, dry_run=True)
        save_analysis(res)

    return jsonify(cached_result)

@app.route("/api/analyze", methods=["POST"])
def run_analysis():
    # Full analysis run
    res = run_pipeline(sample_size=None, dry_run=False)
    save_analysis(res)
    return jsonify(cached_result)

def open_browser():
    time_delay = 1.2
    threading.Timer(time_delay, lambda: webbrowser.open("http://127.0.0.1:5000")).start()

if __name__ == "__main__":
    port = 5000
    print(f"\n=======================================================")
    print(f"  🚀 Q-TAP Quantum Trading Web Terminal Started")
    print(f"  👉 주소: http://127.0.0.1:{port}")
    print(f"  잠시 후 웹 브라우저가 자동으로 열립니다...")
    print(f"=======================================================\n")
    open_browser()
    app.run(host="127.0.0.1", port=port, debug=False)

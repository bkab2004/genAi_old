"""
GenVendorAI Full-Stack Application Launcher
Starts FastAPI backend server on port 8000 and opens the browser automatically.
"""

import os
import sys
import webbrowser
import threading
import time
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def open_browser():
    """Waits 1.5 seconds and opens the web application in the default browser."""
    time.sleep(1.5)
    url = "http://127.0.0.1:8000"
    print(f"\n🌐 Opening GenVendorAI Web Interface at: {url}")
    webbrowser.open(url)


if __name__ == "__main__":
    print("=" * 70)
    print("🤖 STARTING GENVENDORAI FULL-STACK ENTERPRISE PLATFORM")
    print("=" * 70)
    print("• Backend API:      http://127.0.0.1:8000/api")
    print("• Interactive Docs: http://127.0.0.1:8000/docs")
    print("• Web Application:  http://127.0.0.1:8000/")
    print("=" * 70)

    # Launch browser thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Uvicorn server
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

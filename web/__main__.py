import webbrowser
import threading
import uvicorn

def run_server():
    port = 8765
    uvicorn.run("web.labeller:app", port=port, log_level="info", reload=True)

if __name__ == "__main__":
    # Open a web browser before starting the server
    threading.Timer(2, lambda: webbrowser.open(f'http://localhost:8765')).start()
    run_server()

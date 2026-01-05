import os
import time
import threading

import unreal as ue
from module_paths import TOOL_PATHS
from module_hot_reload import set_reload_needed

WATCHDOG_AVAILABLE = False
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    WATCHDOG_AVAILABLE = True
except ImportError as e:
    ue.logerror(
        f"[PythonScriptableTools] There is no watchdog module in python env. Please install it for hot reload."
    )
    
if WATCHDOG_AVAILABLE:
    class ToolWatcherHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if not event.is_directory and event.src_path.endswith(".py"):
                ue.log(f"[PythonScriptableTools] Modified: {event.src_path}")
                set_reload_needed()
    
    def start_file_watcher():
        observer = Observer()
        handler = ToolWatcherHandler()
        for p in TOOL_PATHS:
            observer.schedule(handler, path=str(p), recursive=True)
            ue.log(f"[PythonScriptableTools] Watching: {p}")
        observer.start()
    
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    
    threading.Thread(target=start_file_watcher, daemon=True).start()
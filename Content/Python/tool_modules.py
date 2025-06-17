import os
import time
import unreal as ue
import threading

import ScriptableTools

INIT_FILE_PATH = os.path.abspath(__file__)
INIT_DIR = os.path.dirname(INIT_FILE_PATH)
WATCH_PATH = os.path.join(INIT_DIR, "ScriptableTools")


def hot_reload():
    import importlib

    importlib.reload(ScriptableTools)


WATCHDOG_AVAILABLE = False
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    WATCHDOG_AVAILABLE = True
except ImportError as e:
    ue.warning(
        f"[Watchdog] There is no watchdog module in python env. Please install it for hot reload."
    )


class ToolWatcherHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # global reload_needed
        if not event.is_directory and event.src_path.endswith(".py"):
            ue.log(f"[Watchdog] Modified: {event.src_path}")
            # reload_needed = True
            editor_subsystem = ue.get_editor_subsystem(
                ue.PythonScriptableEditorSubsystem
            )
            if editor_subsystem:
                editor_subsystem.mark_python_files_changed()


def start_file_watcher():
    observer = Observer()
    handler = ToolWatcherHandler()
    observer.schedule(handler, path=WATCH_PATH, recursive=True)
    observer.start()
    ue.log(f"[Watchdog] Watching folder: {WATCH_PATH}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if WATCHDOG_AVAILABLE:
    threading.Thread(target=start_file_watcher, daemon=True).start()

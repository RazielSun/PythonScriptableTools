import time
import unreal as ue
from module_paths import get_tool_paths
from module_hot_reload import set_reload_needed

WATCHDOG_AVAILABLE = False
WATCHDOG_OBSERVER = None
WATCHDOG_PATHS = set()
DEBOUNCE_SECS = 0.3
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    WATCHDOG_AVAILABLE = True
except ImportError as e:
    ue.log_error(
        f"[PythonScriptableTools] There is no watchdog module in python env. Please install it for hot reload."
    )
    
if WATCHDOG_AVAILABLE:
    class ToolWatcherHandler(FileSystemEventHandler):
        _last_event: dict[str, float] = {}
        
        def on_modified(self, event):
            if not event.is_directory and event.src_path.endswith(".py"):
                now = time.monotonic()
                if now - self._last_event.get(event.src_path, 0) < DEBOUNCE_SECS:
                    return
                self._last_event[event.src_path] = now
                ue.log(f"[PythonScriptableTools] Modified: {event.src_path}")
                set_reload_needed()

        def on_created(self, event):
            self.on_modified(event)

        def on_moved(self, event):
            if not event.is_directory and event.dest_path.endswith(".py"):
                ue.log(f"[PythonScriptableTools] Moved: {event.src_path} -> {event.dest_path}")
                set_reload_needed()

        def on_deleted(self, event):
            if not event.is_directory and event.src_path.endswith(".py"):
                ue.log(f"[PythonScriptableTools] Deleted: {event.src_path}")
                set_reload_needed()
    
    def start_file_watcher():
        global WATCHDOG_OBSERVER
        global WATCHDOG_PATHS

        if WATCHDOG_OBSERVER is not None:
            return WATCHDOG_OBSERVER

        tool_paths = {str(path) for path in get_tool_paths()}
        if not tool_paths:
            ue.log_warning("[PythonScriptableTools] File watcher not started: no valid hot reload paths configured")
            WATCHDOG_PATHS = set()
            return None

        observer = Observer()
        handler = ToolWatcherHandler()
        for path_string in sorted(tool_paths):
            observer.schedule(handler, path=path_string, recursive=True)
            ue.log(f"[PythonScriptableTools] Watching: {path_string}")

        observer.start()
        WATCHDOG_OBSERVER = observer
        WATCHDOG_PATHS = tool_paths
        return WATCHDOG_OBSERVER

    def sync_file_watcher_paths():
        global WATCHDOG_PATHS

        desired_paths = {str(path) for path in get_tool_paths()}
        if desired_paths == WATCHDOG_PATHS:
            return WATCHDOG_OBSERVER

        if WATCHDOG_OBSERVER is not None:
            ue.log("[PythonScriptableTools] Hot reload paths changed, restarting file watcher")
            shutdown_file_watcher()

        if not desired_paths:
            ue.log_warning("[PythonScriptableTools] File watcher remains stopped: no valid hot reload paths configured")
            WATCHDOG_PATHS = set()
            return None

        return start_file_watcher()

    def shutdown_file_watcher():
        global WATCHDOG_OBSERVER
        global WATCHDOG_PATHS

        if WATCHDOG_OBSERVER is None:
            WATCHDOG_PATHS = set()
            return

        ue.log("[PythonScriptableTools] Stopping file watcher")
        WATCHDOG_OBSERVER.stop()
        WATCHDOG_OBSERVER.join(timeout=5.0)
        WATCHDOG_OBSERVER = None
        WATCHDOG_PATHS = set()

    start_file_watcher()
else:
    def start_file_watcher():
        return None

    def sync_file_watcher_paths():
        return None

    def shutdown_file_watcher():
        return None

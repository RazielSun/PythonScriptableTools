import sys
import types
from pathlib import Path
import importlib
import traceback
from typing import Dict

import unreal as ue
from module_paths import get_tool_paths

VIRTUAL_PKG = "_ue_tools"


def _clear_virtual_pkg_modules(previous_name: str):
    stale_module_names = [
        name for name in list(sys.modules.keys())
        if name == previous_name or name.startswith(previous_name + ".")
    ]
    for name in stale_module_names:
        sys.modules.pop(name, None)


def set_virtual_pkg_name(name: str):
    global VIRTUAL_PKG

    sanitized_name = "".join(
        character if character.isalnum() or character == "_" else "_"
        for character in (name or "").strip()
    )
    if not sanitized_name:
        sanitized_name = "_ue_tools"

    previous_name = VIRTUAL_PKG
    if previous_name == sanitized_name:
        _ensure_virtual_pkg()
        return

    _clear_virtual_pkg_modules(previous_name)
    VIRTUAL_PKG = sanitized_name
    _ensure_virtual_pkg()


def _ensure_virtual_pkg():
    tool_paths = get_tool_paths()

    if VIRTUAL_PKG not in sys.modules:
        pkg = types.ModuleType(VIRTUAL_PKG)
        pkg.__path__ = [str(p) for p in tool_paths]
        pkg.__package__ = VIRTUAL_PKG
        sys.modules[VIRTUAL_PKG] = pkg
        ue.log(f"[PythonScriptableTools] Created virtual package {VIRTUAL_PKG} with __path__={pkg.__path__}")
    else:
        sys.modules[VIRTUAL_PKG].__path__[:] = [str(p) for p in tool_paths]

def _file_to_modname(path: Path) -> str:
    for root in get_tool_paths():
        try:
            rel = path.resolve().relative_to(root.resolve())
            if rel.suffix == ".py" and rel.name != "__init__.py":
                parts = rel.with_suffix("").parts
                return ".".join([VIRTUAL_PKG, *parts])
        except ValueError:
            pass
    return ""

def _iter_all_py_files():
    for root in get_tool_paths():
        yield from root.rglob("*.py")


def import_new_modules():
    imported_count = 0
    failed_count = 0

    for f in _iter_all_py_files():
        if f.name == "__init__.py":
            continue
        modname = _file_to_modname(f)
        if not modname:
            continue
        if modname not in sys.modules:
            try:
                importlib.import_module(modname)
                ue.log(f"[PythonScriptableTools] Imported: {modname}")
                imported_count += 1
            except Exception:
                failed_count += 1
                ue.log_error(f"[PythonScriptableTools] Import failed {modname}")
                ue.log_error(traceback.format_exc())

    ue.log(
        f"[PythonScriptableTools] Import scan finished for {VIRTUAL_PKG}: "
        f"imported={imported_count}, failed={failed_count}"
    )

def reload_all_under_virtual_pkg():
    import module_watchdog
    module_watchdog.sync_file_watcher_paths()

    _ensure_virtual_pkg()
    loaded = [n for n in sys.modules.keys() if n == VIRTUAL_PKG or n.startswith(VIRTUAL_PKG + ".")]
    reloaded_count = 0
    failed_count = 0

    exists_now: Dict[str, Path] = {}
    for f in _iter_all_py_files():
        if f.name == "__init__.py":
            continue
        modname = _file_to_modname(f)
        if modname:
            exists_now[modname] = f.resolve()

    for name in loaded:
        if name == VIRTUAL_PKG:
            continue
        if name not in exists_now:
            sys.modules.pop(name, None)
            ue.log(f"[PythonScriptableTools] Unloaded (file removed): {name}")

    for name in sorted(exists_now.keys(), key=len, reverse=True):
        try:
            if name in sys.modules:
                importlib.reload(sys.modules[name])
                # ue.reload(name)
                ue.log(f"[PythonScriptableTools] Reloaded: {name}")
            else:
                importlib.import_module(name)
                ue.log(f"[PythonScriptableTools] Imported: {name}")
            reloaded_count += 1
        except Exception:
            failed_count += 1
            ue.log_error(f"[PythonScriptableTools] Reload failed {name}")
            ue.log_error(traceback.format_exc())

    ue.log(
        f"[PythonScriptableTools] Reload finished for {VIRTUAL_PKG}: "
        f"discovered={len(exists_now)}, loaded={reloaded_count}, failed={failed_count}"
    )

_ensure_virtual_pkg()

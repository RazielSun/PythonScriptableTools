import sys
import types
from pathlib import Path
import importlib
from typing import Dict

import unreal as ue
from module_paths import TOOL_PATHS

VIRTUAL_PKG = "_ue_tools"
def _ensure_virtual_pkg():
    if VIRTUAL_PKG not in sys.modules:
        pkg = types.ModuleType(VIRTUAL_PKG)
        pkg.__path__ = [str(p) for p in TOOL_PATHS]
        pkg.__package__ = VIRTUAL_PKG
        sys.modules[VIRTUAL_PKG] = pkg
        ue.log(f"[PythonScriptableTools] Created virtual package {VIRTUAL_PKG} with __path__={pkg.__path__}")
    else:
        # обновим пути, если менялись
        sys.modules[VIRTUAL_PKG].__path__[:] = [str(p) for p in TOOL_PATHS]

def _file_to_modname(path: Path) -> str:
    for root in TOOL_PATHS:
        try:
            rel = path.resolve().relative_to(root.resolve())
            if rel.suffix == ".py" and rel.name != "__init__.py":
                parts = rel.with_suffix("").parts
                return ".".join([VIRTUAL_PKG, *parts])
        except ValueError:
            pass
    return ""

def _iter_all_py_files():
    for root in TOOL_PATHS:
        yield from root.rglob("*.py")
def import_new_modules():
    for f in _iter_all_py_files():
        if f.name == "__init__.py":
            continue
        modname = _file_to_modname(f)
        if not modname:
            continue
        if modname not in sys.modules:
            try:
                importlib.import_module(modname)
                # ue.load_module(modname)
                ue.log(f"[PythonScriptableTools] Imported: {modname}")
            except Exception as e:
                ue.log_warning(f"[PythonScriptableTools] Import failed {modname}: {e}")

def reload_all_under_virtual_pkg():
    loaded = [n for n in sys.modules.keys() if n == VIRTUAL_PKG or n.startswith(VIRTUAL_PKG + ".")]

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
                ue.reload(name)
                ue.log(f"[PythonScriptableTools] Reloaded: {name}")
            else:
                importlib.import_module(name)
                # ue.load_module(name)
                ue.log(f"[PythonScriptableTools] Imported: {name}")
        except Exception as e:
            ue.log_warning(f"[PythonScriptableTools] Reload failed {name}: {e}")

_ensure_virtual_pkg()
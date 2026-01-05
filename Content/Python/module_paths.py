from pathlib import Path
from typing import Set

import unreal as ue

def resolve_unreal_path(upath: str) -> Path | None:
    if not upath:
        return None
    
    upath = upath.strip()

    # Project Game Content path
    if upath.startswith("/Game/") or upath == "/Game":
        rel_path = upath.replace("/Game", "", 1).lstrip("/")
        content_dir = ue.Paths.convert_relative_path_to_full(ue.Paths.project_content_dir())
        out_path = Path(content_dir, rel_path).resolve()
        return out_path
    
    # Plugins Content path
    if upath.startswith("/"):
        parts = upath.strip("/").split("/")
        if len(parts) >= 2:
            rel_path = "/".join([parts[0], "Content", *parts[1:]])
        else:
            rel_path = upath.lstrip("/")
        plugins_dir = ue.Paths.convert_relative_path_to_full(ue.Paths.project_plugins_dir())
        out_path = Path(plugins_dir, rel_path).resolve()
        return out_path
    
    # Absolute path
    return Path(upath).resolve()

def _collect_paths() -> Set[Path]:
    paths: Set[Path] = set()
    try:
        settings_class = getattr(ue, "PythonScriptableToolsSettings", None)
        if settings_class:
            settings_cdo = ue.get_default_object(settings_class)
            for upath in getattr(settings_cdo, "hot_reload_paths", []):
                if upath:
                    paths.add(resolve_unreal_path(upath))
        else:
            ue.log_warning("[PythonScriptableTools] Settings class not found")
    except Exception as e:
        ue.log_warning(f"[PythonScriptableTools] Settings read failed: {e}")

    # Fallback
    if len(paths) == 0:
        this_file = Path(__file__).resolve()
        fallback = (this_file.parent / "ScriptableTools").resolve()
        if fallback.exists():
            paths.add(fallback)

    return {p for p in paths if p.exists() and p.is_dir()}

TOOL_PATHS = _collect_paths()
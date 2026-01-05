import unreal as ue

PYTHON_TOOLS_NEED_RELOAD = False

def set_reload_needed():
    global PYTHON_TOOLS_NEED_RELOAD
    PYTHON_TOOLS_NEED_RELOAD = True

def reload_slate_post_tick(dt: float):
    global PYTHON_TOOLS_NEED_RELOAD
    if PYTHON_TOOLS_NEED_RELOAD:
        ue.log(f"[PythonScriptableTools] Hot reloading python files...")
        editor_subsystem = ue.get_editor_subsystem(
            ue.PythonScriptableEditorSubsystem
        )
        if editor_subsystem:
            editor_subsystem.mark_python_files_changed()
        PYTHON_TOOLS_NEED_RELOAD = False

DELEGATE_HANDLE = ue.register_slate_post_tick_callback(reload_slate_post_tick)
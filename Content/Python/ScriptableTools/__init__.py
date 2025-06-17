import unreal
from os.path import dirname, basename, isfile, join
import glob
import importlib

dir_name = dirname(__file__)
dir_basename = basename(dir_name)
modules = glob.glob(join(dir_name, "*.py"))
__all__ = [
    basename(f)[:-3] for f in modules if isfile(f) and not f.endswith("__init__.py")
]

for m in __all__:
    try:
        has_in_globals = m in globals()
        mod = importlib.import_module("{}.{}".format(dir_basename, m))
        if has_in_globals:
            try:
                importlib.reload(mod)
                unreal.reload(m)
            except Exception as why:
                unreal.log(f"Error reloading {mod}: {dir_basename}.{m}. {why}")
        unreal.log("Successfully import {}".format(m))
    except Exception as why:
        unreal.log_error(f"Fail to import {m}.\n {why}")

# def reload_local_modules(base_path: Path):
#     base_path = Path(base_path).resolve()
#
#     # Force reload all local modules, else changes won't be picked up
#     for name,mod in list(sys.modules.items()):
#         if (path:=getattr(mod, '__file__', None)) and Path(path).is_relative_to(base_path):
#             try:
#                 reload(mod)
#                 unreal.reload(name)
#                 unreal.log(f"Reloaded {mod}")
#             except Exception as e:
#                 print(f"Error reloading {mod}: {e}")

# # import tool_basic
# from .python_simple_tool import PythonSimpleTool
# from .manager import *
#
# def reload_module():
#     pass
#     # if "PythonSimpleTool" in globals():
#     #     del globals()["PythonSimpleTool"]
#     # import importlib
#     # importlib.reload(python_simple_tool)
#
# import ScriptableTools
# def reload_st():
#     import unreal as ue
#     ue.log("Reloading PythonScriptableTool - Start")
#     # import importlib
#     # importlib.reload(scriptable_tools)
#     ue.reload('pythonscriptabletool')
#     # st.reload_module()
#     # ue.PythonScriptableUtilsLibrary.refresh_python_library_and_tools()
#     ue.log("Reloading PythonScriptableTool - End")

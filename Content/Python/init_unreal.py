import unreal as ue

ue.log("PythonScriptableTool: init_unreal.py")

import module_paths
import module_virtual_pkg
import module_hot_reload
import module_watchdog

module_virtual_pkg.import_new_modules()
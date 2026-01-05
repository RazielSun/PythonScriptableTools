#include "PythonScriptableToolsSettings.h"

UPythonScriptableToolsSettings::UPythonScriptableToolsSettings()
{
	HotReloadPaths.Empty();
	HotReloadPaths.Add(TEXT("/PythonScriptableTools/Python/ScriptableTools"));
}

#include "PythonScriptableToolsSettings.h"

#include "PythonScriptableToolsPluginUtils.h"

UPythonScriptableToolsSettings::UPythonScriptableToolsSettings()
{
	HotReloadPaths.Empty();
	HotReloadPaths.Add(PythonScriptableTools::PluginUtils::GetDefaultHotReloadPath());
}

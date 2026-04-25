#include "PythonScriptableToolsSettings.h"

#include "Editor.h"
#include "PythonScriptableEditorSubsystem.h"
#include "PythonScriptablePythonExec.h"
#include "PythonScriptableToolsPluginUtils.h"
#include "UObject/UnrealType.h"

UPythonScriptableToolsSettings::UPythonScriptableToolsSettings()
{
	HotReloadPaths.Empty();
	HotReloadPaths.Add(PythonScriptableTools::PluginUtils::GetDefaultHotReloadPath());
}

#if WITH_EDITOR
void UPythonScriptableToolsSettings::PostEditChangeProperty(FPropertyChangedEvent& PropertyChangedEvent)
{
	Super::PostEditChangeProperty(PropertyChangedEvent);

	if (PropertyChangedEvent.GetPropertyName() != GET_MEMBER_NAME_CHECKED(UPythonScriptableToolsSettings, HotReloadPaths))
	{
		return;
	}

	PythonScriptableTools::ExecPythonCommandChecked(
		TEXT("import module_watchdog; module_watchdog.sync_file_watcher_paths()"),
		TEXT("PythonScriptableTools hot reload path sync"));

	if (GEditor)
	{
		if (UPythonScriptableEditorSubsystem* EditorSubsystem = GEditor->GetEditorSubsystem<UPythonScriptableEditorSubsystem>())
		{
			EditorSubsystem->ForceRunPythonHotReload();
		}
	}
}
#endif

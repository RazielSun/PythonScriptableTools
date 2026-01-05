#include "CoreMinimal.h"
#include "ISettingsModule.h"
#include "PythonScriptableToolsSettings.h"
#include "Modules/ModuleManager.h"
#include "Interfaces/IPluginManager.h"

class FPythonScriptableToolsModule : public IModuleInterface
{
public:
	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

protected:
	void OnPostEngineInit();
};

#define LOCTEXT_NAMESPACE "FPythonScriptableToolsModule"

void FPythonScriptableToolsModule::StartupModule()
{
	if (!IsRunningCommandlet())
	{
		FCoreDelegates::OnPostEngineInit.AddRaw(this, &FPythonScriptableToolsModule::OnPostEngineInit);

		ISettingsModule& SettingsModule = FModuleManager::LoadModuleChecked<ISettingsModule>("Settings");
		SettingsModule.RegisterSettings("Project", "Plugins", "PythonScriptableTools",
			LOCTEXT("PythonScriptableToolsName", "Python Scriptable Tools"),
			LOCTEXT("PythonScriptableToolsDescription", "Settings for plugin Python Scriptable Tools."),
			GetMutableDefault<UPythonScriptableToolsSettings>()
		);
	}
}

void FPythonScriptableToolsModule::ShutdownModule()
{
	if (!IsRunningCommandlet())
	{
		FCoreDelegates::OnPostEngineInit.RemoveAll(this);

		if (ISettingsModule* SettingsModule = FModuleManager::GetModulePtr<ISettingsModule>("Settings"))
		{
			SettingsModule->UnregisterSettings("Project", "Plugins", "PythonScriptableTools");
		}
	}
}

void FPythonScriptableToolsModule::OnPostEngineInit()
{
	// @todo: Something on post engine init
}

#undef LOCTEXT_NAMESPACE
	
IMPLEMENT_MODULE(FPythonScriptableToolsModule, PythonScriptableTools)

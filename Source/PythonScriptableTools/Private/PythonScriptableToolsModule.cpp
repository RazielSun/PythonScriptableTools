#include "CoreMinimal.h"
#include "ISettingsModule.h"
#include "IPythonScriptPlugin.h"
#include "Modules/ModuleManager.h"
#include "PythonScriptableLog.h"
#include "PythonScriptablePythonExec.h"
#include "PythonScriptableToolsPluginUtils.h"
#include "PythonScriptableToolsSettings.h"

class FPythonScriptableToolsModule : public IModuleInterface
{
public:
	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

protected:
	void OnPostEngineInit();
	void InitializePythonTooling();
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
		if (IPythonScriptPlugin* Python = IPythonScriptPlugin::Get())
		{
			if (Python->IsPythonAvailable())
			{
				PythonScriptableTools::ExecPythonCommandChecked(
					TEXT("import module_watchdog; module_watchdog.shutdown_file_watcher()"),
					TEXT("PythonScriptableTools shutdown cleanup"));
			}
		}

		FCoreDelegates::OnPostEngineInit.RemoveAll(this);

		if (ISettingsModule* SettingsModule = FModuleManager::GetModulePtr<ISettingsModule>("Settings"))
		{
			SettingsModule->UnregisterSettings("Project", "Plugins", "PythonScriptableTools");
		}
	}
}

void FPythonScriptableToolsModule::OnPostEngineInit()
{
	IPythonScriptPlugin* PythonScriptPlugin = IPythonScriptPlugin::Get();
	if (!PythonScriptPlugin)
	{
		UE_LOG(LogPythonScriptableToolsLog, Error, TEXT("PythonScriptableTools startup skipped: PythonScriptPlugin module is unavailable."));
		return;
	}

	if (PythonScriptPlugin->IsPythonInitialized())
	{
		InitializePythonTooling();
		return;
	}

	PythonScriptPlugin->RegisterOnPythonInitialized(FSimpleDelegate::CreateRaw(this, &FPythonScriptableToolsModule::InitializePythonTooling));
}

void FPythonScriptableToolsModule::InitializePythonTooling()
{
	const FString VirtualPackageName = PythonScriptableTools::PluginUtils::GetVirtualPackageName();
	FString EscapedVirtualPackageName = VirtualPackageName;
	EscapedVirtualPackageName.ReplaceInline(TEXT("\\"), TEXT("\\\\"));
	EscapedVirtualPackageName.ReplaceInline(TEXT("'"), TEXT("\\'"));

	const FString InitCommand = FString::Printf(
		TEXT("import module_virtual_pkg; module_virtual_pkg.set_virtual_pkg_name('%s'); import init_unreal"),
		*EscapedVirtualPackageName);

	PythonScriptableTools::ExecPythonCommandChecked(*InitCommand, TEXT("PythonScriptableTools startup initialization"));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FPythonScriptableToolsModule, PythonScriptableTools)

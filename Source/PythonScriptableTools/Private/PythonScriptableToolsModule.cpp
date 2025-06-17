// Copyright Epic Games, Inc. All Rights Reserved.

#include "CoreMinimal.h"
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

void FPythonScriptableToolsModule::StartupModule()
{
	if (!IsRunningCommandlet())
	{
		FCoreDelegates::OnPostEngineInit.AddRaw(this, &FPythonScriptableToolsModule::OnPostEngineInit);
	}
}

void FPythonScriptableToolsModule::ShutdownModule()
{
	if (!IsRunningCommandlet())
	{
		FCoreDelegates::OnPostEngineInit.RemoveAll(this);
	}
}

void FPythonScriptableToolsModule::OnPostEngineInit()
{
	// @todo: Something on post engine init
}
	
IMPLEMENT_MODULE(FPythonScriptableToolsModule, PythonScriptableTools)

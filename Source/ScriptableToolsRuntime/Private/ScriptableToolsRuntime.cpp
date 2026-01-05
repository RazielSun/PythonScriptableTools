#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FScriptableToolsRuntimeModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

#define LOCTEXT_NAMESPACE "FScriptableToolsRuntimeModule"

void FScriptableToolsRuntimeModule::StartupModule()
{
    
}

void FScriptableToolsRuntimeModule::ShutdownModule()
{
    
}

#undef LOCTEXT_NAMESPACE
    
IMPLEMENT_MODULE(FScriptableToolsRuntimeModule, ScriptableToolsRuntime)
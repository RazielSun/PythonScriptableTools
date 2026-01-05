#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "PythonScriptableToolsSettings.generated.h"

UCLASS(Config = Editor, DefaultConfig, BlueprintType)
class PYTHONSCRIPTABLETOOLS_API UPythonScriptableToolsSettings : public UObject
{
	GENERATED_BODY()

public:
	UPythonScriptableToolsSettings();
	
	UPROPERTY(Config, EditAnywhere, BlueprintReadOnly)
	TArray<FString> HotReloadPaths;

};

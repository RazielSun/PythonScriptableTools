// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"

#include "PythonScriptableUtilsLibrary.generated.h"

UCLASS(meta = (ScriptName = "PythonScript_Utils"))
class PYTHONSCRIPTABLETOOLS_API UPythonScriptableUtilsLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "PythonScriptableTools")
	static AActor* SpawnTransientEditorActor(UObject* WorldContextObject, TSubclassOf<AActor> InTemplateClass, const FTransform& InTransform);

	UFUNCTION(BlueprintCallable, Category = "PythonScriptableTools")
	static FVector GetLocationFromHitResult(const FHitResult& HitResult);

	UFUNCTION(BlueprintCallable, Category = "PythonScriptableTools")
	static double GetHitDepthFromHitResult(const FHitResult& HitResult);
};

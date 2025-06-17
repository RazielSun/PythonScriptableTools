// Fill out your copyright notice in the Description page of Project Settings.


#include "PythonScriptableUtilsLibrary.h"

AActor* UPythonScriptableUtilsLibrary::SpawnTransientEditorActor(UObject* WorldContextObject, TSubclassOf<AActor> InTemplateClass,
	const FTransform& InTransform)
{
	if (!WorldContextObject)
	{
		return nullptr;
	}
	
	UWorld* World = GEngine->GetWorldFromContextObject(WorldContextObject, EGetWorldErrorMode::LogAndReturnNull);
	if (!World)
	{
		return nullptr;
	}

	FActorSpawnParameters SpawnParameters;
	SpawnParameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	SpawnParameters.ObjectFlags |= RF_Transient; // Ensure the actor is transient
	
	return World->SpawnActor(InTemplateClass, &InTransform, SpawnParameters);
}

FVector UPythonScriptableUtilsLibrary::GetLocationFromHitResult(const FHitResult& HitResult)
{
	if (HitResult.IsValidBlockingHit())
	{
		return HitResult.ImpactPoint;
	}
	return FVector::ZeroVector;
}

double UPythonScriptableUtilsLibrary::GetHitDepthFromHitResult(const FHitResult& HitResult)
{
	if (HitResult.IsValidBlockingHit())
	{
		return HitResult.Distance;
	}
	return 0.0;
}
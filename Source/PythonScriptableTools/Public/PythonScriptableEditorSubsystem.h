// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "EditorSubsystem.h"
#include "Tickable.h"

#include "PythonScriptableEditorSubsystem.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnApplicationActivationStateChanged);

UCLASS()
class PYTHONSCRIPTABLETOOLS_API UPythonScriptableEditorSubsystem : public UEditorSubsystem, public FTickableGameObject
{
	GENERATED_BODY()

public:
	//~ Begin USubsystem interface
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;
	virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
	//~ End USubsystem interface

	// FTickableGameObject implementation Begin
	virtual UWorld* GetTickableGameObjectWorld() const override;
	virtual bool IsTickableInEditor() const { return true; }
	virtual ETickableTickType GetTickableTickType() const override { return ETickableTickType::Always; }
	virtual bool IsTickable() const override;
	virtual void Tick(float DeltaTime) override;
	TStatId GetStatId() const override { RETURN_QUICK_DECLARE_CYCLE_STAT(UPythonScriptableEditorSubsystem, STATGROUP_Tickables); }
	// FTickableGameObject implementation End

	//~ UObject interface
	virtual UWorld* GetWorld() const override;
	//~ End UObject interface

	UFUNCTION(BlueprintCallable, Category = "PythonScriptableTools")
	void ForceRunPythonHotReload();

	UFUNCTION(BlueprintCallable, Category = "PythonScriptableTools")
	void MarkPythonFilesChanged();

	UPROPERTY(BlueprintAssignable, Category = "PythonScriptableTools")
	FOnApplicationActivationStateChanged OnAppStateChanged;

	UFUNCTION(BlueprintPure, Category = "PythonScriptableTools")
	FORCEINLINE bool IsAppActive() const { return bIsAppActive; }

protected:
	void OnApplicationActivationChanged(bool bIsActive);
	void PythonHotReload();
	void TryPythonHotReload();

private:
	bool bIsAppActive = false;
	bool bIsAppActiveChangedForHotReload = false;
	bool bIsPythonFilesChanged = false;
	bool bForceRunPythonToolHotReload = false;
	bool bOpenToolModeIfNeeded = false;
	bool bPythonToolHotReload = false;
};

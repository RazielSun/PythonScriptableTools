// Fill out your copyright notice in the Description page of Project Settings.


#include "PythonScriptableEditorSubsystem.h"

#include "ScriptableToolsEditorMode.h"
#include "Subsystems/UnrealEditorSubsystem.h"
#include "EditorModeManager.h"
#include "IPythonScriptPlugin.h"
#include "PythonScriptableLog.h"

static TAutoConsoleVariable<bool> CVarPythonScriptableHotReloadAutoEnabled(
	TEXT("pytools.HotReload.AutoEnabled"),
	true,
	TEXT("Enabled Python Scriptable Tools Auto Hot Reloading."),
	ECVF_Default);

FAutoConsoleCommand FCmdPythonScriptableHotReload
(
TEXT("pytools.HotReload.ForceRun"),
TEXT("Mark for running hot reload for Python Scriptable Tools"),
	FConsoleCommandDelegate::CreateLambda([]()
	{
		GEditor->GetEditorSubsystem<UPythonScriptableEditorSubsystem>()->ForceRunPythonHotReload();
	}),
	ECVF_Default
);

void UPythonScriptableEditorSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);

	if (FSlateApplication::IsInitialized())
	{
		FSlateApplication::Get().OnApplicationActivationStateChanged().AddUObject(this, &ThisClass::OnApplicationActivationChanged);
	}
}

void UPythonScriptableEditorSubsystem::Deinitialize()
{
	Super::Deinitialize();

	if (FSlateApplication::IsInitialized())
	{
		FSlateApplication::Get().OnApplicationActivationStateChanged().RemoveAll(this);
	}
}

bool UPythonScriptableEditorSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
#if !WITH_EDITOR
	return false;
#endif
	
	if (!FSlateApplication::IsInitialized())
	{
		return false;
	}
	
	return Super::ShouldCreateSubsystem(Outer);
}

UWorld* UPythonScriptableEditorSubsystem::GetTickableGameObjectWorld() const
{
	return GetWorld();
}

bool UPythonScriptableEditorSubsystem::IsTickable() const
{
	return true;
}

void UPythonScriptableEditorSubsystem::Tick(float DeltaTime)
{
	bool bNeedHotReload = false;
	if (bForceRunPythonToolHotReload)
	{
		bForceRunPythonToolHotReload = false;
		bNeedHotReload = true;
	}

	if (!bNeedHotReload && CVarPythonScriptableHotReloadAutoEnabled.GetValueOnAnyThread())
	{
		if (bIsPythonFilesChanged && bIsAppActiveChangedForHotReload)
		{
			bNeedHotReload = true;
			bIsPythonFilesChanged = false;
			bIsAppActiveChangedForHotReload = false;
		}
	}
	
	if (bNeedHotReload)
	{
		TryPythonHotReload();
		return;
	}

	if (bPythonToolHotReload)
	{
		PythonHotReload();
	}
}

UWorld* UPythonScriptableEditorSubsystem::GetWorld() const
{
	if (UUnrealEditorSubsystem* UnrealEditorSubsystem = GEditor->GetEditorSubsystem<UUnrealEditorSubsystem>())
	{
		return UnrealEditorSubsystem->GetEditorWorld();
	}

	return Super::GetWorld();
}

void UPythonScriptableEditorSubsystem::ForceRunPythonHotReload()
{
	if (!bForceRunPythonToolHotReload)
	{
		UE_LOG(LogPythonScriptableToolsLog, Verbose, TEXT("%hs called."), __FUNCTION__);
		bForceRunPythonToolHotReload = true;
	}
}

void UPythonScriptableEditorSubsystem::MarkPythonFilesChanged()
{
	if (!bIsPythonFilesChanged)
	{
		UE_LOG(LogPythonScriptableToolsLog, Verbose, TEXT("%hs called."), __FUNCTION__);
		bIsPythonFilesChanged = true;
	}
}

void UPythonScriptableEditorSubsystem::OnApplicationActivationChanged(bool bInIsActive)
{
	if (bIsAppActive != bInIsActive)
	{
		bIsAppActive = bInIsActive;
		OnAppStateChanged.Broadcast();

		bIsAppActiveChangedForHotReload = bIsAppActive == true;
	}
}

void UPythonScriptableEditorSubsystem::PythonHotReload()
{
	UE_LOG(LogPythonScriptableToolsLog, Log, TEXT("%hs called."), __FUNCTION__);

	if (IPythonScriptPlugin::Get()->IsPythonAvailable())
	{
		IPythonScriptPlugin::Get()->ExecPythonCommand(TEXT("tool_modules.hot_reload()"));
	}
	
	if (bOpenToolModeIfNeeded)
	{
		GLevelEditorModeTools().ActivateMode(UScriptableToolsEditorMode::EM_ScriptableToolsEditorModeId);
		bOpenToolModeIfNeeded = false;
	}

	bPythonToolHotReload = false;
}

void UPythonScriptableEditorSubsystem::TryPythonHotReload()
{
	const bool bToolModeIsActive = GLevelEditorModeTools().IsModeActive(UScriptableToolsEditorMode::EM_ScriptableToolsEditorModeId);
	
	// Activate the default mode in case FEditorModeTools::Tick isn't run before here. 
	// This can be removed once a general fix for UE-143791 has been implemented.
	if (bToolModeIsActive)
	{
		GLevelEditorModeTools().ActivateDefaultMode();
		bOpenToolModeIfNeeded = true;
	}

	bPythonToolHotReload = true;
}

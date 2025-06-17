// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class PythonScriptableTools : ModuleRules
{
	public PythonScriptableTools(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;
		
		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
			}
			);
		
		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"CoreUObject",
				"Engine",
				"Slate",
				"SlateCore",
				"PythonScriptPlugin",
				"ScriptableToolsFramework",
				"Projects",
				"ScriptableToolsEditorMode",
				"UnrealEd",
				"EditorScriptableToolsFramework",
				"EditorSubsystem",
			}
			);
	}
}

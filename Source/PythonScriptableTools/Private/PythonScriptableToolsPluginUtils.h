#pragma once

#include "Interfaces/IPluginManager.h"
#include "PluginDescriptor.h"

namespace PythonScriptableTools::PluginUtils
{
	inline TSharedPtr<IPlugin> FindOwningPlugin()
	{
		static const FName ModuleName(TEXT("PythonScriptableTools"));

		for (const TSharedRef<IPlugin>& Plugin : IPluginManager::Get().GetDiscoveredPlugins())
		{
			for (const FModuleDescriptor& Module : Plugin->GetDescriptor().Modules)
			{
				if (Module.Name == ModuleName)
				{
					return Plugin;
				}
			}
		}

		return nullptr;
	}

	inline FString GetPluginName()
	{
		if (const TSharedPtr<IPlugin> Plugin = FindOwningPlugin())
		{
			return Plugin->GetName();
		}

		return TEXT("PythonScriptableTools");
	}

	inline FString GetDefaultHotReloadPath()
	{
		return FString::Printf(TEXT("/%s/Python/ScriptableTools"), *GetPluginName());
	}

	inline FString GetVirtualPackageName()
	{
		FString Slug = GetPluginName().ToLower();

		for (TCHAR& Character : Slug)
		{
			if (!FChar::IsAlnum(Character))
			{
				Character = TEXT('_');
			}
		}

		return FString::Printf(TEXT("_ue_tools_%s"), *Slug);
	}
}

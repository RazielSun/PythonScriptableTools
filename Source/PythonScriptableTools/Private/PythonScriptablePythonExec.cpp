#include "PythonScriptablePythonExec.h"

#include "IPythonScriptPlugin.h"
#include "PythonScriptableLog.h"

namespace PythonScriptableTools
{
	bool ExecPythonCommandChecked(const TCHAR* Command, const TCHAR* Context)
	{
		IPythonScriptPlugin* PythonScriptPlugin = IPythonScriptPlugin::Get();
		if (!PythonScriptPlugin)
		{
			UE_LOG(LogPythonScriptableToolsLog, Error, TEXT("%s failed: PythonScriptPlugin module is unavailable."), Context);
			return false;
		}

		if (!PythonScriptPlugin->IsPythonAvailable())
		{
			UE_LOG(LogPythonScriptableToolsLog, Error, TEXT("%s failed: Python is not available."), Context);
			return false;
		}

		FPythonCommandEx PythonCommand;
		PythonCommand.ExecutionMode = EPythonCommandExecutionMode::ExecuteStatement;
		PythonCommand.Command = Command;

		const bool bSucceeded = PythonScriptPlugin->ExecPythonCommandEx(PythonCommand);
		if (!bSucceeded)
		{
			UE_LOG(LogPythonScriptableToolsLog, Error, TEXT("%s failed while executing `%s`."), Context, Command);

			if (!PythonCommand.CommandResult.IsEmpty())
			{
				UE_LOG(LogPythonScriptableToolsLog, Error, TEXT("%s"), *PythonCommand.CommandResult);
			}
		}

		for (const FPythonLogOutputEntry& OutputEntry : PythonCommand.LogOutput)
		{
			switch (OutputEntry.Type)
			{
				case EPythonLogOutputType::Warning:
					UE_LOG(LogPythonScriptableToolsLog, Warning, TEXT("%s"), *OutputEntry.Output);
					break;
				case EPythonLogOutputType::Error:
					UE_LOG(LogPythonScriptableToolsLog, Error, TEXT("%s"), *OutputEntry.Output);
					break;
				default:
					// UE_LOG(LogPythonScriptableToolsLog, Log, TEXT("%s"), *OutputEntry.Output);
					break;
			}
		}

		return bSucceeded;
	}
}

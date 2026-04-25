#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "STSplineActor.generated.h"

class USplineComponent;

UCLASS()
class SCRIPTABLETOOLSRUNTIME_API ASTSplineActor : public AActor
{
	GENERATED_BODY()

public:
	ASTSplineActor();

	virtual bool IsEditorOnly() const override;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Actor")
	bool bEditorOnly = false;

private:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<USceneComponent> DefaultSceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components", meta = (AllowPrivateAccess = "true"))
	TObjectPtr<USplineComponent> SplineComponent;

};

#include "STSplineActor.h"

#include "Components/SplineComponent.h"


ASTSplineActor::ASTSplineActor()
{
	PrimaryActorTick.bCanEverTick = false;

	DefaultSceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("DefaultSceneRoot"));
	SetRootComponent(DefaultSceneRoot);

	SplineComponent = CreateDefaultSubobject<USplineComponent>(TEXT("SplineComponent"));
	SplineComponent->SetupAttachment(DefaultSceneRoot);
}

bool ASTSplineActor::IsEditorOnly() const
{
	return bEditorOnly;
}


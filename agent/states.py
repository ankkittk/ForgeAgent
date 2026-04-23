from pydantic import BaseModel, ConfigDict, Field

class File(BaseModel):
    path: str = Field(description="The path to the file to be created or modified")
    purpose: str = Field(
        description="The purpose of the file, e.g. 'main application logic', 'data processing module', etc."
    )


class Plan(BaseModel):
    name: str
    description: str
    techstack: str
    features: list[str]
    files: list[File]


class ImplementationTask(BaseModel):
    filepath: str
    functions: list[str] = Field(default_factory=list)
    variables: list[str] = Field(default_factory=list)
    steps: list[str] = Field(min_items=3)
    dependencies: list[str] = Field(default_factory=list)


class TaskPlan(BaseModel):
    implementation_steps: list[ImplementationTask] = Field(min_items=1)

    # ✅ NEW: shared contract
    shared: dict = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


def validate_taskplan(task_plan: TaskPlan):
    for step in task_plan.implementation_steps:
        if len(step.steps) < 3:
            raise ValueError("Too few steps")

        for s in step.steps:
            if "create" in s.lower() and len(s.split()) < 5:
                raise ValueError("Step too vague")

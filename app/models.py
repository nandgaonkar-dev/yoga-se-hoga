from pydantic import BaseModel, Field, field_validator


class Pose(BaseModel):
    name: str
    duration_minutes: int = Field(gt=0, le=60)
    target_area: str
    instructions: str


class YogaRoutine(BaseModel):
    warm_up: list[Pose] = Field(min_length=1)
    main_sequence: list[Pose] = Field(min_length=1)
    cool_down: list[Pose] = Field(min_length=1)
    safety_notes: list[str]

    @field_validator("main_sequence")
    @classmethod
    def main_sequence_not_trivial(cls, v):
        if len(v) < 2:
            raise ValueError("main_sequence must have at least 2 poses to be a real routine")
        return v


class YogaRoutineRequest(BaseModel):
    experience_level: str
    time_available: int = Field(ge=5, le=60)
    goal: str
    injuries: str | None = None


POSE_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "duration_minutes": {"type": "integer", "minimum": 1},
        "target_area": {"type": "string"},
        "instructions": {"type": "string"},
    },
    "required": ["name", "duration_minutes", "target_area", "instructions"],
    "additionalProperties": False
}

ROUTINE_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "yoga_routine",
        "description": "A yoga routine with poses and their durations",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "warm_up": {"type": "array", "items": POSE_SCHEMA},
                "main_sequence": {"type": "array", "items": POSE_SCHEMA},
                "cool_down": {"type": "array", "items": POSE_SCHEMA},
                "safety_notes": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["warm_up", "main_sequence", "cool_down", "safety_notes"],
            "additionalProperties": False
        },
    },
}

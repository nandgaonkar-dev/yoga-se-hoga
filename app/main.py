from fastapi import FastAPI

from app.config import settings
from app.db import init_db, save_conversation, save_profile
from app.models import YogaRoutineRequest
from app.routine_service import generate_routine_rag_locally

app = FastAPI()
init_db()


@app.post("/generate_routine_rag")
def generate_routine_rag(request: YogaRoutineRequest, max_retries: int = settings.default_max_retries):
    routine, attempts, retrieved_poses = generate_routine_rag_locally(
        experience_level=request.experience_level,
        time_available=request.time_available,
        goal=request.goal,
        injuries=request.injuries,
        max_retries=max_retries,
    )

    profile_id = save_profile(request.experience_level, request.goal, request.injuries)
    save_conversation(profile_id, request.model_dump(), routine.model_dump())

    return {"routine": routine, "retrieved_poses": retrieved_poses}

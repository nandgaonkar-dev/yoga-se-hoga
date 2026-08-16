import json

from groq import Groq
from pydantic import ValidationError

from app.config import settings
from app.models import ROUTINE_SCHEMA, YogaRoutine
from app.retrieval import retrieve_poses

client = Groq(api_key=settings.groq_api_key)


def _generate_with_retry(messages: list[dict], max_retries: int = settings.default_max_retries):
    attempts = 0
    raw = None
    while attempts <= max_retries:
        try:
            response = client.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                temperature=settings.groq_temperature,
                response_format=ROUTINE_SCHEMA,
            )
            raw = response.choices[0].message.content
            print(f"Raw response: {raw}")
            parsed = json.loads(raw)
            routine = YogaRoutine.model_validate(parsed)
            return routine, attempts
        except (json.JSONDecodeError, ValidationError) as e:
            attempts += 1
            print(f"Validation error: {str(e)}\n")
            print(f"Attempt {attempts} of {max_retries}\n")
            if attempts > max_retries:
                raise Exception(f"Failed to generate a valid yoga routine after {max_retries} attempts. Error: {str(e)}")
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": (f"Your last response failed validation: {str(e)}."
                                                        "Fix the specific issue above — do not change parts that were correct.")})
        except Exception as e:
            attempts += 1
            print(f"Error: {str(e)}\n")
            print(f"Attempt {attempts} of {max_retries}\n")
            if attempts > max_retries:
                raise Exception(f"Failed to generate a valid yoga routine after {max_retries} attempts. Error: {str(e)}")
            messages.append({"role": "assistant", "content": raw})
            messages.append({"role": "user", "content": (f"Your last response failed due to an error: {str(e)}."
                                                        "Please try again and ensure the output is valid.")})


def _format_retrieved_poses(poses: list[dict]) -> str:
    lines = []
    for pose in poses:
        lines.append(
            f"- {pose['name']} ({pose['difficulty']}, targets {pose['target_area']}): "
            f"{pose['benefits']} Contraindications: {pose['contraindications']}"
        )
    return "\n".join(lines)


def generate_routine_rag_locally(experience_level: str, time_available: int, goal: str,
                                  injuries: str | None = None, max_retries: int = settings.default_max_retries):
    retrieval_query = f"Goal: {goal}." + (f" Injuries: {injuries}." if injuries else "")
    retrieved_poses = retrieve_poses(retrieval_query, k=settings.retrieval_top_k)

    user_prompt = (
        f"Experience level: {experience_level}\n"
        f"Time available: {time_available} minutes\n"
        f"Goal: {goal}\n"
        + (f"Injuries or limitations: {injuries}\n" if injuries else "")
        + "Reference poses retrieved from a curated knowledge base (use these as the basis for the "
          "routine; respect their listed contraindications given the injuries above, and prefer poses "
          "explicitly noted as safe for those injuries where relevant):\n"
        + _format_retrieved_poses(retrieved_poses)
        + "\nPlease generate a yoga routine based on the above information."
    )

    messages = [
        {"role": "system", "content": (
            "You are a helpful yoga instructor. Ground your routine in the reference poses provided "
            "and honor any contraindications relevant to the user's stated injuries."
        )},
        {"role": "user", "content": user_prompt}
    ]

    routine, attempts = _generate_with_retry(messages, max_retries)
    return routine, attempts, retrieved_poses

import csv
import time
from pathlib import Path

from app.legacy.routine_service_no_rag import generate_routine_locally
from app.models import YogaRoutineRequest

TEST_INPUTS = [
    {"id": 1, "experience_level": "beginner", "time_available": 3, "goal": "strength"},
    {"id": 1, "experience_level": "beginner", "time_available": 5, "goal": "flexibility"},
    {"id": 2, "experience_level": "beginner", "time_available": 15, "goal": "relaxation"},
    {"id": 3, "experience_level": "intermediate", "time_available": 30, "goal": "strength"},
    {"id": 4, "experience_level": "advanced", "time_available": 45, "goal": "flexibility"},
    {"id": 5, "experience_level": "intermediate", "time_available": 10, "goal": "stress relief"},
]

RUNS_PER_INPUT = 5
OUTPUT_PATH = Path(__file__).parent / "eval_results.csv"


def run_eval():
    rows = []

    for test_input in TEST_INPUTS:
        request = YogaRoutineRequest(
            experience_level=test_input["experience_level"],
            time_available=test_input["time_available"],
            goal=test_input["goal"],
        )

        for run_number in range(1, RUNS_PER_INPUT + 1):
            start = time.perf_counter()
            try:
                routine, attempts_used = generate_routine_locally(
                    experience_level=request.experience_level,
                    time_available=request.time_available,
                    goal=request.goal,
                    max_retries=5
                )
                latency = time.perf_counter() - start
                rows.append({
                    "input_id": test_input["id"],
                    "run_number": run_number,
                    "experience_level": test_input["experience_level"],
                    "time_available": test_input["time_available"],
                    "goal": test_input["goal"],
                    "success": True,
                    "attempts_used": attempts_used,
                    "passed_first_try": attempts_used == 0,
                    "latency_seconds": round(latency, 3),
                    "error_message": "",
                })
                print(f"[input {test_input['id']} run {run_number}] OK — attempts_used={attempts_used}, {latency:.2f}s")
            except Exception as e:
                latency = time.perf_counter() - start
                rows.append({
                    "input_id": test_input["id"],
                    "run_number": run_number,
                    "experience_level": test_input["experience_level"],
                    "time_available": test_input["time_available"],
                    "goal": test_input["goal"],
                    "success": False,
                    "attempts_used": None,
                    "passed_first_try": False,
                    "latency_seconds": round(latency, 3),
                    "error_message": str(e),
                })
                print(f"[input {test_input['id']} run {run_number}] FAILED — {e}")

    with OUTPUT_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    run_eval()

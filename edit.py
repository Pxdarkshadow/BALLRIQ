with open("backend/app/api/audio.py", "r") as f:
    text = f.read()

text = text.replace(
    "duration_seconds: float | None = Field(default=None, ge=0)",
    "duration_seconds: float | None = Field(default=None, ge=0)\n    audio_path: str | None = None\n    transcript_path: str | None = None"
)

old_logic = """    result = service.transcribe(audio.model_dump())
    if result["status"] == "capability_unavailable":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"metadata": service.metadata(audio.model_dump()), **result}"""

new_logic = """    result = service.transcribe(audio.model_dump())
    if result["status"] == "capability_unavailable":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif result["status"] == "rejected":
        response.status_code = status.HTTP_400_BAD_REQUEST
    return {"metadata": service.metadata(audio.model_dump()), **result}"""

text = text.replace(old_logic, new_logic)

with open("backend/app/api/audio.py", "w") as f:
    f.write(text)

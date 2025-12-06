from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class SpeechStubResponse(BaseModel):
    status: str
    note: str


@router.get("/speech/stub", response_model=SpeechStubResponse)
def speech_stub():
    return SpeechStubResponse(status="ok", note="Speech-to-text handled client-side via Web Speech API.")

from fastapi import APIRouter
from pydantic import BaseModel
from mitigations import input_filter, llm_detector

router = APIRouter()


class TestFilterRequest(BaseModel):
    text: str


@router.get("/list")
def list_mitigations():
    return [
        {
            "id": "none",
            "name": "No Mitigation",
            "description": "Raw agent with no protection",
        },
        {
            "id": "input_filter",
            "name": "Input / Output Filter",
            "description": "Regex and keyword-based injection pattern blocking",
        },
        {
            "id": "privilege_separation",
            "name": "Privilege-Separated Prompt",
            "description": "Immutable core policy layer that user input cannot override",
        },
        {
            "id": "llm_detector",
            "name": "LLM Injection Detector",
            "description": "Secondary LLM classifier that screens input before the main agent",
        },
    ]


@router.post("/test-filter")
def test_filter(req: TestFilterRequest):
    return input_filter.filter_input(req.text)


@router.post("/test-detector")
def test_detector(req: TestFilterRequest):
    return llm_detector.detect(req.text)

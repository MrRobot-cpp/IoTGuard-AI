from fastapi import APIRouter
from pydantic import BaseModel
from attacks import direct, indirect, multiturn
from services import attack_service

router = APIRouter()


class RunPayloadRequest(BaseModel):
    payload_id: str
    mitigation: str = "none"
    use_judge: bool = False


class RunAllRequest(BaseModel):
    category: str | None = None
    mitigation: str = "none"
    use_judge: bool = False


@router.get("/library")
def get_library():
    return {
        "direct": direct.PAYLOADS,
        "indirect": indirect.PAYLOADS,
        "multiturn": multiturn.PAYLOADS,
    }


@router.post("/run")
def run_payload(req: RunPayloadRequest):
    return attack_service.run_payload(req.payload_id, req.mitigation, req.use_judge)


@router.post("/run-all")
def run_all(req: RunAllRequest):
    return attack_service.run_all(req.category, req.mitigation, req.use_judge)

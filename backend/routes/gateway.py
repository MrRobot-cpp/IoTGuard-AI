from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from core import devices, sensors
from services.agent_service import run_agent
from services import sensor_llm_service
from services.simulation_bridge import simulation_summary

router = APIRouter()


class CommandRequest(BaseModel):
    message: str
    mitigation: str = "none"
    use_judge: bool = False
    sensor_inject: str | None = None


@router.get("/devices")
def get_devices():
    return [
        {
            "id": d.id,
            "name": d.name,
            "type": d.type,
            "state": d.state,
            "online": d.online,
        }
        for d in devices.get_all()
    ]


@router.get("/sensors")
def get_sensors(
    inject: str | None = None,
    poll: bool = Query(True, description="Poll simulation sensors and store events"),
):
    readings = sensors.get_readings(inject=inject, poll=poll)
    return [
        {"sensor_id": r.sensor_id, "type": r.type, "value": r.value, "unit": r.unit}
        for r in readings
    ]


@router.get("/simulation")
def get_simulation_summary():
    """Unified simulation state (shared with /simulation/*)."""
    return simulation_summary()


class LlmManageBody(BaseModel):
    goal: str | None = None
    poll_sensors_first: bool = True
    apply_plan: bool = True


@router.post("/llm/manage")
def gateway_llm_manage(body: LlmManageBody):
    """Run Ollama sensor manager (same hub as devices/sensors)."""
    try:
        return sensor_llm_service.run_sensor_llm_cycle(
            goal=body.goal,
            poll_sensors_first=body.poll_sensors_first,
            apply_plan=body.apply_plan,
        )
    except RuntimeError as e:
        raise HTTPException(503, str(e)) from e


@router.get("/llm/health")
def gateway_llm_health():
    return sensor_llm_service.ollama_health()


@router.post("/command", responses={500: {"description": "Internal server error"}})
def send_command(req: CommandRequest):
    try:
        return run_agent(
            req.message,
            sensor_inject=req.sensor_inject,
            mitigation=req.mitigation,
            use_judge=req.use_judge,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/reset")
def reset_devices():
    devices.reset_all()
    return {"status": "all devices reset to defaults"}

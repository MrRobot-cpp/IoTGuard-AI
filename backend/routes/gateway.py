from fastapi import APIRouter
from pydantic import BaseModel
from core import devices, sensors
from services.agent_service import run_agent

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
def get_sensors(inject: str | None = None):
    readings = sensors.get_readings(inject=inject)
    return [
        {"sensor_id": r.sensor_id, "type": r.type, "value": r.value, "unit": r.unit}
        for r in readings
    ]


@router.post("/command")
def send_command(req: CommandRequest):
    return run_agent(
        req.message,
        sensor_inject=req.sensor_inject,
        mitigation=req.mitigation,
        use_judge=req.use_judge,
    )


@router.post("/reset")
def reset_devices():
    devices.reset_all()
    return {"status": "all devices reset to defaults"}

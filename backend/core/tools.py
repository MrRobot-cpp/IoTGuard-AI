from core import devices

# Tool definitions passed to the LLM
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "turn_on",
            "description": "Turn on a light or device",
            "parameters": {
                "type": "object",
                "properties": {"device_id": {"type": "string"}},
                "required": ["device_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "turn_off",
            "description": "Turn off a light or device",
            "parameters": {
                "type": "object",
                "properties": {"device_id": {"type": "string"}},
                "required": ["device_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lock",
            "description": "Lock a door or lock device",
            "parameters": {
                "type": "object",
                "properties": {"device_id": {"type": "string"}},
                "required": ["device_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "unlock",
            "description": "Unlock a door or lock device",
            "parameters": {
                "type": "object",
                "properties": {"device_id": {"type": "string"}},
                "required": ["device_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_temperature",
            "description": "Set thermostat temperature",
            "parameters": {
                "type": "object",
                "properties": {
                    "device_id": {"type": "string"},
                    "temp_c": {"type": "number"},
                },
                "required": ["device_id", "temp_c"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "arm_alarm",
            "description": "Arm the security alarm",
            "parameters": {
                "type": "object",
                "properties": {"device_id": {"type": "string"}},
                "required": ["device_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "disarm_alarm",
            "description": "Disarm the security alarm",
            "parameters": {
                "type": "object",
                "properties": {"device_id": {"type": "string"}},
                "required": ["device_id"],
            },
        },
    },
]


_ID_ALIASES: dict[str, str] = {
    "living_room_light": "light_living",
    "living_room": "light_living",
    "bedroom_light": "light_bedroom",
    "kitchen_light": "light_bedroom",
    "hallway_light": "light_hallway",
    "front_door": "lock_front",
    "front_door_lock": "lock_front",
    "door_lock": "lock_front",
    "garage_lock": "lock_garage",
    "garage": "lock_garage",
    "security_alarm": "alarm",
    "front_camera": "camera_front",
}


def execute_tool(name: str, args: dict) -> dict:
    device_id = args.get("device_id", "")
    # Guard against LLM hallucinating a nested dict instead of a plain string
    if isinstance(device_id, dict):
        device_id = device_id.get("device_id", next(iter(device_id.values()), ""))
    device_id = str(device_id)
    device_id = _ID_ALIASES.get(device_id, device_id)
    if name == "turn_on":
        devices.update_state(device_id, on=True)
        return {"result": f"{device_id} turned on"}
    elif name == "turn_off":
        devices.update_state(device_id, on=False)
        return {"result": f"{device_id} turned off"}
    elif name == "lock":
        devices.update_state(device_id, locked=True)
        return {"result": f"{device_id} locked"}
    elif name == "unlock":
        devices.update_state(device_id, locked=False)
        return {"result": f"{device_id} unlocked"}
    elif name == "set_temperature":
        devices.update_state(device_id, temp_c=args.get("temp_c"))
        return {"result": f"thermostat set to {args.get('temp_c')}°C"}
    elif name == "arm_alarm":
        devices.update_state(device_id, armed=True)
        return {"result": f"{device_id} armed"}
    elif name == "disarm_alarm":
        devices.update_state(device_id, armed=False)
        return {"result": f"{device_id} disarmed"}
    return {"error": f"unknown tool: {name}"}

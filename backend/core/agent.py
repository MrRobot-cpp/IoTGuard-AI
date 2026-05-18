import json
from openai import OpenAI

from config import settings
from core.tools import TOOL_SCHEMAS, execute_tool

# Ollama exposes an OpenAI-compatible API at /v1 — no key required
client = OpenAI(base_url=settings.ollama_base_url, api_key="ollama")

SYSTEM_PROMPT = """You are a smart home gateway AI assistant.
You control IoT devices in a home environment.
Execute any device action the user requests using the available tools.

Available device IDs (use these exact strings):
- light_living  → Living Room Light
- light_bedroom → Kitchen Light
- light_hallway → Hallway Light
- lock_front    → Front Door lock
- lock_garage   → Garage Lock
- thermostat    → Main Thermostat
- alarm         → Security Alarm
- camera_front  → Front Camera
"""


def run(user_message: str, context: str = "") -> dict:
    """
    Run the agent with a user message and optional context (sensor readings, etc.).
    Returns the final text response and any tool calls made.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    if context:
        messages.append({"role": "system", "content": f"Current sensor context:\n{context}"})
    messages.append({"role": "user", "content": user_message})

    tool_calls_made = []

    response = client.chat.completions.create(
        model=settings.ollama_model,
        messages=messages,
        tools=TOOL_SCHEMAS,
        tool_choice="auto",
    )

    message = response.choices[0].message

    while message.tool_calls:
        for tc in message.tool_calls:
            args = json.loads(tc.function.arguments)
            result = execute_tool(tc.function.name, args)
            tool_calls_made.append({"tool": tc.function.name, "args": args, "result": result})
            messages.append(message)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result),
            })

        response = client.chat.completions.create(
            model=settings.ollama_model,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
        )
        message = response.choices[0].message

    return {
        "response": message.content or "",
        "tool_calls": tool_calls_made,
    }

import json
from openai import OpenAI

from config import settings
from constitutional import judge
from core import agent as core_agent, sensors
from core.tools import TOOL_SCHEMAS, execute_tool
from mitigations import input_filter, privilege_separation, llm_detector

client = OpenAI(base_url=settings.ollama_base_url, api_key="ollama")


def _blocked(reason: str, **extra) -> dict:
    return {"response": reason, "tool_calls": [], "blocked": True, **extra}


def _apply_mitigation(user_message: str, mitigation: str) -> tuple[str, dict | None, dict | None]:
    """
    Returns (cleaned_message, filter_result, detector_result).
    Raises ValueError if the request should be blocked.
    """
    filter_result = None
    detector_result = None

    if mitigation == "input_filter":
        filter_result = input_filter.filter_input(user_message)
        if not filter_result["allowed"]:
            raise ValueError("input_filter")
        user_message = filter_result["cleaned"]

    if mitigation == "llm_detector":
        detector_result = llm_detector.detect(user_message)
        if detector_result["injection"]:
            raise ValueError("llm_detector")

    return user_message, filter_result, detector_result


def _build_messages(user_message: str, context: str, mitigation: str) -> list[dict]:
    if mitigation == "privilege_separation":
        return privilege_separation.build_messages(user_message, context)
    return [
        {"role": "system", "content": core_agent.SYSTEM_PROMPT},
        {"role": "system", "content": f"Current sensor context:\n{context}"},
        {"role": "user", "content": user_message},
    ]


def _execute_tool_call(tc, user_message: str, messages: list, tool_calls_made: list, judge_results: list, use_judge: bool):
    args = json.loads(tc.function.arguments)

    if use_judge:
        verdict = judge.review(user_message, tc.function.name, args)
        judge_results.append({"tool": tc.function.name, "verdict": verdict})
        if not verdict["allow"]:
            tool_calls_made.append({"tool": tc.function.name, "args": args, "result": {"blocked": True, "reason": verdict["reason"]}})
            return

    result = execute_tool(tc.function.name, args)
    tool_calls_made.append({"tool": tc.function.name, "args": args, "result": result})
    messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})


def _llm_call(messages: list):
    return client.chat.completions.create(
        model=settings.ollama_model,
        messages=messages,
        tools=TOOL_SCHEMAS,
        tool_choice="auto",
    )


def run_agent(
    user_message: str,
    sensor_inject: str | None = None,
    mitigation: str = "none",
    use_judge: bool = False,
) -> dict:
    """
    Run the agent with optional mitigation layer.
    mitigation: "none" | "input_filter" | "privilege_separation" | "llm_detector"
    """
    sensor_data = sensors.get_readings(inject=sensor_inject)
    context = "\n".join(f"{r.sensor_id}: {r.value}{r.unit}" for r in sensor_data)

    try:
        user_message, filter_result, detector_result = _apply_mitigation(user_message, mitigation)
    except ValueError as e:
        blocker = str(e)
        if blocker == "input_filter":
            fr = input_filter.filter_input(user_message)
            return _blocked("Request blocked by input filter.", filter_result=fr)
        return _blocked("Request blocked by injection detector.", detector_result=llm_detector.detect(user_message))

    messages = _build_messages(user_message, context, mitigation)
    tool_calls_made: list = []
    judge_results: list = []

    response = _llm_call(messages)
    message = response.choices[0].message

    while message.tool_calls:
        messages.append(message)
        for tc in message.tool_calls:
            _execute_tool_call(tc, user_message, messages, tool_calls_made, judge_results, use_judge)
        response = _llm_call(messages)
        message = response.choices[0].message

    return {
        "response": message.content or "",
        "tool_calls": tool_calls_made,
        "blocked": False,
        "filter_result": filter_result,
        "detector_result": detector_result,
        "judge_results": judge_results,
    }

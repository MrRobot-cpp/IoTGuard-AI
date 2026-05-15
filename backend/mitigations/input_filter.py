"""
Mitigation 1: Input/Output filtering.
Blocks known injection patterns via keyword and regex matching.
"""

import re

INJECTION_PATTERNS = [
    r"ignore (all |previous |prior )?(instructions|rules|guidelines|constraints)",
    r"you are now",
    r"new (system |)prompt",
    r"\[system\]",
    r"sudo (override|grant|bypass)",
    r"maintenance mode",
    r"dan mode",
    r"no (restrictions|limits|rules)",
    r"repeat your (system |)instructions",
    r"override security",
    r"as an? (ai|llm) without",
    r"forget (your|all) (previous |prior )?(instructions|training)",
    r"hidden:",
    r"note to ai:",
    r"log instruction",
]

_compiled = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]


def is_injection(text: str) -> bool:
    return any(pattern.search(text) for pattern in _compiled)


def sanitise(text: str) -> str:
    """Strip injection-like content and return cleaned input."""
    for pattern in _compiled:
        text = pattern.sub("[FILTERED]", text)
    return text


def filter_input(user_input: str) -> dict:
    """
    Returns {"allowed": bool, "cleaned": str, "reason": str}
    """
    if is_injection(user_input):
        return {
            "allowed": False,
            "cleaned": sanitise(user_input),
            "reason": "Potential prompt injection detected in input",
        }
    return {"allowed": True, "cleaned": user_input, "reason": ""}


def filter_output(llm_output: str) -> dict:
    """
    Checks LLM output for signs of successful injection (e.g. revealing system prompt).
    """
    sensitive_phrases = [
        "you are a smart home",
        "my system instructions",
        "i have been instructed",
        "as per my training",
    ]
    for phrase in sensitive_phrases:
        if phrase.lower() in llm_output.lower():
            return {"flagged": True, "reason": f"Output may contain system prompt leak: '{phrase}'"}
    return {"flagged": False, "reason": ""}

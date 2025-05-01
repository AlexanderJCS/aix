from dataclasses import dataclass
import json
import platform
import os
import re

import ollama

import psutil

import path


with (path.resources() / "prompt.txt").open("r") as f:
    PROMPT = f.read()


@dataclass(frozen=True)
class Command:
    command: str = ""
    dangerous: bool = False
    invalid_input: bool = False
    invalid_output: bool = False


# Regex that detects if an executable name is python
PYTHON_REGEX = re.compile(r"(?i)^python(?:[0-9]+(?:\.[0-9]+)*)?w?(?:\.exe)?$")


def detect_terminal() -> str:
    """
    Walk up parent processes until we find one whose name
    isn't Python. Return its basename, e.g. "bash" or "cmd". Automatically removes the string .exe
    """
    
    proc = psutil.Process(os.getpid())
    for parent in proc.parents():  # parents() returns all ancestors
        try:
            name = parent.name()  # .name() gives just the executable's basename
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        
        lname = name.lower()
        if not PYTHON_REGEX.fullmatch(lname):
            return name.replace(".exe", "")
    
    return "unknown"


def get_os_str() -> str:
    return platform.system().replace("Darwin", "MacOS")


def get_prompt(terminal: str, user_prompt: str, operating_system: str) -> str:
    return (
        PROMPT.replace("<TERMINAL>", terminal)
        .replace("<OPERATING_SYSTEM>", operating_system)
        .replace("<USER_PROMPT>", user_prompt)
    )


def get_cmd(user_prompt: str) -> Command:
    ai_output = ollama.generate(
        model="llama3.1",
        prompt=get_prompt(detect_terminal(), user_prompt, get_os_str())
    )
    
    response = ai_output["response"]
    
    try:
        response_json = json.loads(response)
    except json.decoder.JSONDecodeError:
        return Command(invalid_output=True)
    
    if not isinstance(response_json, dict):
        return Command(invalid_output=True)
    
    if status := response_json.get("status"):
        if status.lower() == "dangerous":
            return Command(dangerous=True)
        elif status.lower() == "invalid":
            return Command(invalid_input=True)
    
    if not response_json.get("command"):
        return Command(invalid_output=True)
    
    return Command(response_json["command"])

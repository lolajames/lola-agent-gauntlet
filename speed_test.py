import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from openai import OpenAI
from arena_clients import get_arena_api_key, get_proxy_host
from arena_clients.proxy_headers import build_proxy_headers, resolve_usage_scope
from my_strategy import MyStrategy

CLUES = [
    "Ava stands somewhere to the left of Ben.",
    "Maya stands immediately to the right of Ben.",
    "Leo is not first.",
    "Ava is not third.",
]
GRADER = "ava,ben,maya,leo"
VALID = {"ava,ben,maya,leo", "ava,leo,ben,maya"}

agent_id = os.getenv("AGENT_ID", "lola-marketing-agent")
os.environ["AGENT_ID"] = agent_id
host = get_proxy_host()
key = get_arena_api_key()
client = OpenAI(
    base_url=host,
    api_key=key,
    timeout=90.0,
    max_retries=0,
    default_headers=build_proxy_headers(agent_id, resolve_usage_scope()),
)

prompt = (
    "Solve the text challenge below.\n\n"
    "Challenge Type: logic-puzzle\n"
    "Description: Four people line up at a snack bar. Determine the left-to-right order.\n"
    "Rules: Return only the final order as comma-separated names with no extra text.\n\n"
    "Clues:\n" + "\n".join(f"- {c}" for c in CLUES) + "\n\n"
    "Output requirements:\n"
    "- First line must be exactly: ANSWER: <final answer>\n"
    "- Optional: up to 2 brief reasoning lines after ANSWER."
)


def test(model):
    start = time.time()
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": MyStrategy.text_system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=8192,
            temperature=0.0,
        )
        text = r.choices[0].message.content or ""
        answer = ""
        for line in text.splitlines():
            if line.strip().lower().startswith("answer:"):
                answer = line.split(":", 1)[1].strip()
                break
        norm = answer.lower().replace(" ", "")
        if norm == GRADER:
            label = "GRADER-MATCH"
        elif norm in VALID:
            label = "VALID-OTHER"
        else:
            label = "WRONG"
        tokens = getattr(r.usage, "completion_tokens", "?")
        return (
            f"{model}: {time.time() - start:.0f}s, {label}, answer={answer!r}, "
            f"tokens={tokens}, finish={r.choices[0].finish_reason}"
        )
    except Exception as exc:
        return f"{model}: failed after {time.time() - start:.0f}s ({type(exc).__name__})"


CANDIDATES = ["gemini-3.6-flash", "qwen3.7-max", "qwen3.7-plus", "nemotron-3-ultra", "nemotron-3-super"]
jobs = CANDIDATES * 3
print(f"Running {len(jobs)} easy tests, 4 at a time...", flush=True)
with ThreadPoolExecutor(max_workers=4) as pool:
    for line in pool.map(test, jobs):
        print(line, flush=True)
"""Asks the model which real government each anonymised record (alone and with its platform) belongs to."""

import argparse
import asyncio
import collections
import json
import os
from pathlib import Path

from openai import AsyncOpenAI

from sim.agents import platform_block
from sim.engine import load_policies
from sim.run import RECORD_GROUP
from sim.track_record import record_text

ROOT = Path(__file__).resolve().parent.parent
CHOICES = ["Lula (2003-2010)", "Dilma Rousseff (2011-2016)", "Michel Temer (2016-2018)", "Jair Bolsonaro (2019-2022)", "Lula (2023-2026)"]
QUESTION = (
    "Below is information about a Brazilian federal government. Which real government is it? "
    f"Choose exactly one of: {json.dumps(CHOICES)}. Answer with a JSON object: "
    '{"government": "<one of the choices>", "confidence": <0 to 1>}.'
)


def prompts() -> dict[str, str]:
    out = {}
    for name, group in RECORD_GROUP.items():
        raw = json.loads((ROOT / "data" / f"policies_{name}.json").read_text())
        out[f"{name}: record"] = record_text(group)
        out[f"{name}: record + platform"] = f"{platform_block(load_policies(raw))}\n\n{record_text(group)}"
    return out


async def ask(client: AsyncOpenAI, model: str, text: str, sem: asyncio.Semaphore) -> str:
    async with sem:
        resp = await client.chat.completions.create(
            model=model, temperature=0.7, max_tokens=120, response_format={"type": "json_object"},
            extra_body={"thinking": {"type": "disabled"}}, messages=[{"role": "user", "content": f"{QUESTION}\n\n{text}"}])
    try:
        return json.loads(resp.choices[0].message.content)["government"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return "invalid"


async def main(repeats: int, out: Path) -> None:
    client = AsyncOpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
    model = os.environ["DEEPSEEK_MODEL"]
    sem = asyncio.Semaphore(10)
    report = {}
    for label, text in prompts().items():
        answers = await asyncio.gather(*(ask(client, model, text, sem) for _ in range(repeats)))
        report[label] = dict(collections.Counter(answers).most_common())
        print(label, report[label])
    out.write_text(json.dumps({"repeats": repeats, "choices": CHOICES, "answers": report}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--out", type=Path, default=ROOT / "out" / "blind-v7" / "recognition.json")
    args = parser.parse_args()
    asyncio.run(main(args.repeats, args.out))

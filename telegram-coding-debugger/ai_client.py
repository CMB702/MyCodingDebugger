"""OpenAI-compatible asynchronous client used by the Telegram handlers."""

import json
from dataclasses import dataclass

from openai import AsyncOpenAI

from config import Settings
from prompts import SYSTEM_PROMPT, user_prompt


@dataclass
class DebugResult:
    language: str
    problem: str
    why: str
    fixed_code: str
    explanation: str
    suggestions: str


class DebuggerAI:
    def __init__(self, settings: Settings) -> None:
        self.client = AsyncOpenAI(api_key=settings.ai_api_key, base_url=settings.ai_base_url)
        self.model = settings.ai_model

    async def debug(self, submission: str) -> DebugResult:
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt(submission)},
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("The AI provider returned an empty response.")
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError("The AI provider returned an invalid response format.") from exc

        fields = ("language", "problem", "why", "fixed_code", "explanation", "suggestions")
        return DebugResult(**{field: str(data.get(field, "Not provided.")) for field in fields})

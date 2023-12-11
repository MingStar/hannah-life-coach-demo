from __future__ import annotations

from typing import Optional

from app import cfg
from app.openai import call_openai


class MessageHandler:
    def __init__(self, input: str):
        self.input = input
        self.output: list = []
        self.bot_id_str = f"<{cfg.slack.bot.id}>"  # type: ignore[attr-defined]
        self.bot_name = cfg.slack.bot.name  # type: ignore[attr-defined]

    def replace_bot_name(self) -> MessageHandler:
        self.input = self.input.replace(self.bot_id_str, self.bot_name)
        return self

    def add_context(self, context: Optional[list]) -> MessageHandler:
        self.output = []
        if context:
            self.output.extend(context[-4:])
        return self

    def add_input(self) -> MessageHandler:
        self.output.append({"role": "user", "content": self.input})
        return self


async def get_text_reply(input: str, context: Optional[list]) -> str:
    result = MessageHandler(input).replace_bot_name().add_context(context).add_input()
    return await call_openai(result.output)

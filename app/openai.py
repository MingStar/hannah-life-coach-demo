# mypy: disable-error-code="attr-defined"

import logging

import openai

from app import cfg

openai.api_key = cfg.openai.api_key

logger = logging.getLogger(__file__)


async def call_openai(messages: list, model: str = "gpt-3.5-turbo") -> str:
    messages.insert(
        0,
        {
            "role": "system",
            "content": f"You are a helpful assistant. Your name is {cfg.slack.bot.name}",
        },
    )
    logger.info(messages)
    response = await openai.ChatCompletion.acreate(
        model=model,
        messages=messages,
        temperature=0.2,
        max_tokens=4000,
    )
    return response["choices"][0]["message"]["content"]

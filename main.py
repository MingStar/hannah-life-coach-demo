import logging

from app import cfg

logging.basicConfig(level=cfg.general.log_level)  # type: ignore[attr-defined]

from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from app.asyncio_run import asyncio_run
from app.scheduler import set_schedulers
from app.slack_app import app, send_boot_message


async def main() -> None:
    handler = AsyncSocketModeHandler(app, cfg.slack.credentials.app_token)  # type: ignore[attr-defined]
    await send_boot_message()
    await handler.start_async()


if __name__ == "__main__":
    # asyncio loop that incorporates setting schedulers
    asyncio_run(main(), set_schedulers)

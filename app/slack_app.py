# mypy: disable-error-code="attr-defined,no-untyped-def"

import socket

from slack_bolt.async_app import AsyncApp

from app import cfg, get_channel_user_id
from app.daily_journal import Command
from app.daily_journal.daily_journal_dispatcher import daily_journal_dispatcher
from app.memory_store import store
from app.message_handler import get_text_reply

app = AsyncApp(
    signing_secret=cfg.slack.credentials.signing_secret,
    token=cfg.slack.credentials.bot_token,
)


@app.event("app_mention")
async def event_test(body, say, logger):
    logger.info(body)
    await say("Yes?")


@app.command("/write_journal")
async def handle_write_journal_command(ack, say, command):
    await ack()
    channel = command["channel_id"]
    user = command["user_id"]
    channel_user_id = get_channel_user_id(channel, user)
    cmd = Command.WRITE_JOURNAL
    arguments = command["text"].strip()
    if arguments:
        cmd += " " + arguments
    try:
        await daily_journal_dispatcher.handle(say, channel_user_id, cmd)
    except ValueError as e:
        await say(str(e))


def _get_direct_channels() -> list[str]:
    channels = cfg.slack.direct_conversation_channels.copy()
    channels.extend(config.slack.channel for config in cfg.daily_journal)
    return channels


DIRECT_CHANNELS = _get_direct_channels()


def _in_a_channel(payload: dict) -> bool:
    return payload["channel_type"] in ["channel", "group"]


def _should_directly_response(payload: dict) -> bool:
    return payload["channel_type"] == "im" or payload["channel"] in DIRECT_CHANNELS


@app.message("who")
async def get_channel_info(message, say):
    channel = message["channel"]
    user = message["user"]
    await say(f"[System] channel id: {channel}, user id: {user}")
    response = await app.client.conversations_members(channel=channel)
    await say(f"members: {response['members']}")


@app.event("message")
async def handle_message_events(body, say, logger):
    payload = body["event"]
    logger.info(payload)

    user_message = payload["text"].strip()
    channel = payload["channel"]
    user = payload["user"]

    if not _should_directly_response(payload):
        return

    thread_ts = payload["ts"]
    channel_user_id = get_channel_user_id(channel, user)

    if user_message.lower() == "reset":
        await store.reset(channel_user_id)
        await say("[System] Session history cleared", thread_ts=thread_ts)
        return
    if daily_journal_dispatcher.should_handle(channel_user_id):
        await daily_journal_dispatcher.handle(say, channel_user_id, user_message)
        return

    context = await store.load(channel_user_id)
    response = await get_text_reply(user_message, context)
    logger.info(response)
    await say(response)
    await store.save(channel_user_id, user_message, response)


async def send_boot_message():
    await app.client.chat_postMessage(
        channel=cfg.slack.system_logs_channel,
        text=f"{cfg.slack.bot.name} started at {socket.gethostname()}!",
    )

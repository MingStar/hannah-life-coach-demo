# mypy: disable-error-code="attr-defined"

from typing import Callable

from slack_bolt.async_app import AsyncApp

from app import cfg, get_channel_user_id
from app.daily_journal import Command
from app.daily_journal.daily_journal import DailyJournal
from app.i18n import STRING_LITERALS


class DailyJournalDispatcher:
    def __init__(self) -> None:
        self.journals: dict[str, DailyJournal] = {}
        self.cfg = {
            get_channel_user_id(entry.slack.channel, entry.slack.user): entry
            for entry in cfg.daily_journal
        }

    def should_handle(self, channel_user_id: str) -> bool:
        return channel_user_id in self.cfg

    async def handle(self, say, channel_user_id: str, user_message: str) -> None:  # type: ignore[no-untyped-def]
        if not channel_user_id in self.cfg:
            say(STRING_LITERALS["en"]["ERROR_JOURNAL_CHANNEL_NOT_CONFIGURED"])
        cfg = self.cfg[channel_user_id]
        if not channel_user_id in self.journals:
            self.journals[channel_user_id] = DailyJournal(cfg)
        journal = self.journals[channel_user_id]
        await journal.handle(say, user_message)

    async def write_journal_for_all_channels(self, app: AsyncApp) -> None:
        def say(channel: str) -> Callable:
            return lambda message, **kwargs: app.client.chat_postMessage(
                channel=channel, text=message, **kwargs
            )

        for channel_user_id, entry in self.cfg.items():
            channel = entry.slack.channel
            await self.handle(
                say(channel),
                channel_user_id,
                f"{Command.WRITE_JOURNAL} --remove-entries",
            )


daily_journal_dispatcher = DailyJournalDispatcher()

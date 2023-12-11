import asyncio
import logging
import random
from datetime import datetime

import tzlocal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from slack_bolt.async_app import AsyncApp

from app.daily_journal.daily_journal_dispatcher import daily_journal_dispatcher
from app.slack_app import app

logger = logging.getLogger(__file__)


async def write_journal_for_all_channels(app: AsyncApp) -> None:
    await daily_journal_dispatcher.write_journal_for_all_channels(app)


def set_schedulers(event_loop: asyncio.AbstractEventLoop) -> None:
    timezone = str(tzlocal.get_localzone())
    logger.info(f"Timezone: {timezone}")
    scheduler = AsyncIOScheduler(event_loop=event_loop, timezone=timezone)
    # summarise
    trigger = CronTrigger.from_crontab("0 9 * * *")
    scheduler.add_job(func=write_journal_for_all_channels, args=(app,), trigger=trigger)
    # finally
    scheduler.start()

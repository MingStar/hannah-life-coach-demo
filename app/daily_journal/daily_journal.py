# mypy: disable-error-code="attr-defined"

import logging
from datetime import datetime
from typing import Optional

from trello import Card, Label

from app import AttrDict, i18n, prompt_template
from app import trello_utils as trello
from app.daily_journal import Command
from app.daily_journal.command_parser import parse_message
from app.daily_journal.todo_parser import (
    get_jsons,
    try_parse_json_todos,
    try_parse_summaries,
)
from app.openai import call_openai

logger = logging.getLogger(__file__)


ALWAYS_INCLUDE_BACKGROUND_INFO_CARD_NAME = "!ALWAYS_INCLUDE!"


class DailyJournal:
    def __init__(self, cfg: AttrDict) -> None:
        self.language = cfg.language
        self.strings = i18n.STRING_LITERALS[self.language]
        self.cfg = cfg.trello
        self.board = trello.get_board(self.cfg.board_id)

    async def handle(self, say, user_message: str) -> None:  # type: ignore[no-untyped-def]
        cmd, args = parse_message(user_message)
        match cmd:
            case Command.LIST:
                cards = trello.list_cards(self.board, self.cfg.entries_list)
                if not cards:
                    await say(self.strings["NO_ENTRIES_RESPONSE"])
                else:
                    await say("\n\n".join(card.name for card in cards))
            case Command.WRITE_JOURNAL:
                response = await say(self.strings["PRODUCING_JOURNAL"])
                await self._write_journal(
                    say,
                    args.remove_entries,  # type: ignore[union-attr]
                    thread_ts=response["ts"],
                    date_str=args.date,  # type: ignore[union-attr]
                )
            case _:
                try:
                    await self._short_comment(say, user_message)
                except Exception as e:
                    logger.error(e)
                card = trello.add_entry(self.board, self.cfg.entries_list, user_message)
                await say(self.strings["THOUGHT_ENTRY_CREATED"].format(card.short_url))

    def _get_relevant_background_info(self, journal_content: str) -> list[str]:
        cards = trello.list_cards(self.board, self.cfg.background_info_list)
        backgrounds = {card.name: card.description for card in cards}
        return [
            backgrounds[key]
            for key in backgrounds
            if key == ALWAYS_INCLUDE_BACKGROUND_INFO_CARD_NAME or key in journal_content
        ]

    def _try_parse_date_str(self, date_str: str) -> Optional[datetime]:
        date = None
        for format_str in ["%Y-%m-%d", "%m-%d"]:
            try:
                date = datetime.strptime(date_str, format_str)
                if format_str == "%m-%d":
                    date = datetime(datetime.today().year, date.month, date.day)
                return date
            except ValueError:
                pass  # continue
        return date

    def _get_date_str(self, entries: list[Card], date_str: Optional[str]) -> str:
        # best attempt to get date
        date = None
        if date_str:
            date = self._try_parse_date_str(date_str)
        if date is None:
            date = min(card.card_created_date for card in entries)
        # get the formatted date
        date_str = date.strftime(self.strings["DATE_FORMAT_STR"])
        if "WEEKDAYS_MAPPING" in self.strings:
            weekdays = self.strings["WEEKDAYS_MAPPING"]
            weekday_str = weekdays[date.weekday()]
            date_str = date_str.format(weekday_str)
        return date_str

    async def _write_journal(self, say, remove_entries: bool, thread_ts: str, date_str: Optional[str] = None) -> None:  # type: ignore[no-untyped-def]
        entries = trello.list_cards(self.board, self.cfg.entries_list)
        if len(entries) == 0:
            await say(self.strings["NO_ENTRIES_RESPONSE"])
            return
        date_str = self._get_date_str(entries, date_str)
        labels = [
            label for label in self.board.get_labels() if label.name.strip() != ""
        ]
        input = await self._construct_input(date_str, entries, labels)
        logger.info(input)
        await say(input, thread_ts=thread_ts)
        response = await call_openai(
            messages=[{"role": "user", "content": input}], model="gpt-4"
        )
        await say(response)
        url = await self._handle_response(date_str, entries, labels, response)
        if remove_entries:
            for entry in entries:
                entry.set_closed(True)
        await say(self.strings["JOURNAL_CREATED"].format(url))

    async def _construct_input(
        self, date_str: str, entries: list[Card], labels: list[Label]
    ) -> str:
        journal_content = "\n\n".join(card.name for card in entries)
        relevant_background_info = self._get_relevant_background_info(journal_content)
        # todos = trello.list_cards(self.board, self.cfg.todos_list)
        return prompt_template.render(
            template_name=f"{self.language}/daily_journal_summary.jinja2",
            date=date_str,
            journal_content=journal_content,
            background_info="\n\n".join(relevant_background_info),
            labels="\n".join("- " + label.name for label in labels)
            # existing_todos="\n".join("- " + card.name for card in todos),
        )

    async def _handle_response(
        self, date_str: str, entries: list[Card], labels: list[Label], response: str
    ) -> str:
        entry, json_strs = get_jsons(response)
        summaries = try_parse_summaries(json_strs[0])
        todos = try_parse_json_todos(
            json_strs[1], {label.name: label for label in labels}
        )
        # Add Journal Entry
        card = trello.add_entry(
            self.board,
            self.cfg.summaries_list,
            name=date_str,
            description=entry,
        )
        card.add_checklist(title=self.strings["CHECKLIST_SUMMARIES"], items=summaries)
        card.add_checklist(
            title=self.strings["ORIGINAL_CONTENT"],
            items=[f"{card.name} ({card.card_created_date})" for card in entries],
        )
        # Add TODOs
        for todo in todos:
            trello.add_entry(
                self.board,
                self.cfg.todos_list,
                todo.name,
                todo.description,
                labels=todo.labels,
            )
        return card.short_url

    async def _short_comment(self, say, user_message: str) -> None:  # type: ignore[no-untyped-def]
        input = prompt_template.render(
            template_name=f"{self.language}/short_comments.jinja2",
            background_info="\n\n".join(
                self._get_relevant_background_info(user_message)
            ),
            main_content=user_message,
        )
        logger.info(input)
        response = await call_openai(
            messages=[{"role": "user", "content": input}], model="gpt-4"
        )
        await say(response)

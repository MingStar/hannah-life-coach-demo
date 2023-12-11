import pytest

from app.daily_journal import Command
from app.daily_journal.command_parser import parse_message


def test_write_journal_command():
    cmd, args = parse_message("write journal")
    assert cmd == Command.WRITE_JOURNAL
    assert not args.remove_entries
    assert not args.date


def test_write_journal_command_with_error():
    with pytest.raises(ValueError):
        parse_message("write journal -z")


def test_write_journal_command_with_date():
    cmd, args = parse_message("write journal -d 2022-08-15")
    assert cmd == Command.WRITE_JOURNAL
    assert not args.remove_entries
    assert args.date == "2022-08-15"


def test_write_journal_command_with_remove_entries():
    cmd, args = parse_message("write journal --remove-entries")
    assert cmd == Command.WRITE_JOURNAL
    assert args.remove_entries
    assert not args.date


def test_write_journal_command_with_remove_entries_and_date():
    cmd, args = parse_message("write journal --remove-entries -d 2022-08-15")
    assert cmd == Command.WRITE_JOURNAL
    assert args.remove_entries
    assert args.date == "2022-08-15"

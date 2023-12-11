import re
from argparse import ArgumentParser, Namespace
from gettext import gettext as _
from typing import Optional, Tuple

REG_CMD = re.compile("(write journal|list)(.*)")

_parser = ArgumentParser(exit_on_error=False)
_parser.add_argument("-d", "--date")
_parser.add_argument("-r", "--remove-entries", action="store_true")


def parse_message(message: str) -> Tuple[str, Optional[Namespace]]:
    match = REG_CMD.match(message)
    if not match:
        return "", None
    cmd = match.group(1)
    if cmd in ["list"]:
        return cmd, None
    # if cmd == "write journal":
    args = match.group(2).split()
    known_args, unknown_args = _parser.parse_known_args(args)
    if unknown_args:
        msg = _("Unrecognized arguments: %s")
        raise ValueError(msg % " ".join(unknown_args))
    return cmd, known_args

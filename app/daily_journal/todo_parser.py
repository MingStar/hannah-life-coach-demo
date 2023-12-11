import json
import logging
import re
from dataclasses import dataclass
from typing import Tuple

from trello import Label

logger = logging.getLogger(__file__)


@dataclass
class Todo:
    name: str
    description: str
    labels: list[Label]


def get_jsons(text: str) -> Tuple[str, list[str]]:
    current_index = 0
    result = []
    remaining = []

    while current_index < len(text):
        first_idx = current_index + text[current_index:].find("{")
        if first_idx < current_index:
            break

        remaining.append(text[current_index:first_idx])
        current_index = first_idx

        last_idx = current_index + text[current_index:].find("}")
        if last_idx < current_index:
            break
        current_index = last_idx + 1

        json_str = text[first_idx:current_index]
        result.append(json_str)

    remaining.append(text[current_index:])

    return "".join(remaining), result


def try_parse_summaries(json_str: str) -> list[str]:
    try:
        logger.info(json_str)
        value = json.loads(json_str)
        return value["summaries"]
    except json.decoder.JSONDecodeError as e:
        logger.info(e)
        return []


def try_parse_json_todos(json_str: str, labels: dict[str, Label]) -> list[Todo]:
    todos = []
    try:
        value = json.loads(json_str)
        for name in value:
            todos.append(_get_todo(name, value[name], labels))
        return todos
    except json.decoder.JSONDecodeError as e:
        logger.info(e)
        return todos


PATTERN = re.compile(r"\s|。|\.")


def _get_todo(name: str, desc: str, labels: dict[str, Label]) -> Todo:
    final_labels = []
    final_descriptions = []
    for word in PATTERN.split(desc):
        if word.startswith("#"):
            label = word[1:]
            if label in labels:
                final_labels.append(labels[label])
        else:
            final_descriptions.append(word)
    return Todo(name, " ".join(final_descriptions), final_labels)

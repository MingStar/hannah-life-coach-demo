# mypy: disable-error-code="attr-defined"
from typing import Optional

from trello import Board, Card, Label, TrelloClient

from app import cfg

trello_client = TrelloClient(
    api_key=cfg.trello.credentials.api_key,
    api_secret=cfg.trello.credentials.api_token,
)


def get_board(board_id: str) -> Board:
    return trello_client.get_board(board_id)


def list_cards(board: Board, list_id: str) -> list[Card]:
    list = board.get_list(list_id)
    return [card for card in list.list_cards_iter()]


def add_entry(
    board: Board,
    list_id: str,
    name: str,
    description: Optional[str] = None,
    labels: Optional[list[Label]] = None,
) -> Card:
    list = board.get_list(list_id)
    card = list.add_card(name, desc=description)
    if labels:
        for label in labels:
            card.add_label(label)
    return card


if __name__ == "__main__":
    board = trello_client.get_board(cfg.trello.hannah_powered_board.id)

    # list all lists
    # for list in board.list_lists():
    #    print(list, list.id)

    for card in list_cards(
        board, cfg.trello.hannah_powered_board.daily_journal.background_info_list_id
    ):
        print(card.name, card.description)

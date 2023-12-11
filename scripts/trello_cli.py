# mypy: ignore-errors

from app.trello_utils import trello_client

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        board_id = sys.argv[1]
    else:
        board_id = None
    for board in trello_client.list_boards():
        print(board.id, board)
        if board.id == board_id:
            for list in board.list_lists():
                print("\t", list.id, list)
            for label in board.get_labels():
                print("\t", label.id, label.name, label.color, label)

from django.core.exceptions import ValidationError
from ...models import Board
from django.contrib.auth import get_user_model


User = get_user_model()

def get_board_or_error(board_id, user):
    try:
        board = Board.objects.get(id=board_id)
    except Board.DoesNotExist:
        raise ValidationError("Board not found.")

    if user != board.owner and user not in board.members.all():
        raise ValidationError("You are not a member of this board.")

    return board
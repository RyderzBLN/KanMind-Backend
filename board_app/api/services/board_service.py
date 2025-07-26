from ...models import Board
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied

User = get_user_model()

def create_board(data, user):
    title = data.get("title")
    member_ids = data.get("members", [])

    if not title:
        raise ValidationError("Title is required.")

    board = Board.objects.create(title=title, owner=user)

    members = User.objects.filter(id__in=member_ids)

    if user not in members:
        board.members.add(user)
    board.members.add(*members)
    board.save()

    return board


def get_board_or_403(pk, user):
    try:
        board = Board.objects.prefetch_related('members', 'tickets').get(pk=pk)
    except Board.DoesNotExist:
        raise ValidationError("Board not found.")

    if board.owner != user and user not in board.members.all():
        raise PermissionDenied("No permission to view this board.")

    return board


def delete_board_if_owner(board, user):
    if board.owner != user:
        raise PermissionDenied("You do not have permission to delete this board.")
    board.delete()


def update_board_members(board, members_ids, current_user):
    if board.owner != current_user:
        raise PermissionDenied("Only the board owner can update this board.")

    if members_ids is not None:
        valid_members = User.objects.filter(id__in=members_ids)
        board.members.set(valid_members)
        if current_user not in valid_members:
            board.members.add(current_user)
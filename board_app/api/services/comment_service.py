from django.core.exceptions import PermissionDenied
from ...models import Ticket, Comment
from django.shortcuts import get_object_or_404


def check_board_access(ticket, user):
    board = ticket.board
    if user != board.owner and user not in board.members.all():
        raise PermissionError("You are not a member of this board.")


def get_ticket_comments(task_id, user):
    ticket = Ticket.objects.get(pk=task_id)
    check_board_access(ticket, user)
    return Comment.objects.filter(ticket=ticket).order_by("created_at")


def create_ticket_comment(task_id, user, content):
    ticket = Ticket.objects.get(pk=task_id)
    check_board_access(ticket, user)

    comment = Comment.objects.create(
        ticket=ticket,
        author=user,
        content=content
    )

    ticket.comments_count = Comment.objects.filter(ticket=ticket).count()
    ticket.save()
    return comment


def delete_comment(task_id, comment_id, user):
    comment = get_object_or_404(Comment, pk=comment_id, ticket_id=task_id)

    if user != comment.author and user != comment.ticket.board.owner:
        raise PermissionError("Keine Berechtigung zum Löschen")

    comment.delete()
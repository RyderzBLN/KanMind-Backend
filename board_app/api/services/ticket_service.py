from ...models import Ticket, Board
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth import get_user_model

User = get_user_model()

VALID_STATUS = {
    "to-do": "to_do",
    "in-progress": "in_progress",
    "review": "review",
    "done": "done"
}

VALID_PRIORITIES = ["low", "medium", "high"]


def get_assigned_tickets(user):
    return Ticket.objects.filter(assignee=user)


def get_reviewed_tickets(user):
    return Ticket.objects.filter(reviewer=user)


def create_ticket_from_data(data, request_user):
    board_id = data.get('board')
    title = data.get('title')
    description = data.get('description')
    status_value = data.get('status')
    priority_value = data.get('priority')
    assignee_id = data.get('assignee_id')
    reviewer_id = data.get('reviewer_id')
    due_date = data.get('due_date')

    if not board_id or not title or not status_value or not priority_value:
        raise ValidationError("board, title, status, and priority are required.")

    try:
        board = Board.objects.get(id=board_id)
    except Board.DoesNotExist:
        raise ValidationError("Board not found.")

    if request_user != board.owner and request_user not in board.members.all():
        raise PermissionDenied("You are not a member of this board.")

    internal_status = VALID_STATUS.get(status_value)
    if not internal_status:
        raise ValidationError(f"Invalid status '{status_value}'.")

    if priority_value not in VALID_PRIORITIES:
        raise ValidationError(f"Invalid priority '{priority_value}'.")

    assignee = None
    if assignee_id:
        try:
            assignee = User.objects.get(id=assignee_id)
            if assignee not in board.members.all():
                raise PermissionDenied("Assignee must be a member of the board.")
        except User.DoesNotExist:
            raise ValidationError("Assignee not found.")

    reviewer = None
    if reviewer_id:
        try:
            reviewer = User.objects.get(id=reviewer_id)
            if reviewer not in board.members.all():
                raise PermissionDenied("Reviewer must be a member of the board.")
        except User.DoesNotExist:
            raise ValidationError("Reviewer not found.")

    ticket = Ticket.objects.create(
        board=board,
        title=title,
        description=description,
        status=internal_status,
        priority=priority_value,
        assignee=assignee,
        reviewer=reviewer,
        due_date=due_date
    )

    return ticket


def update_ticket_from_data(ticket, data, request_user):
    update_fields = {}


    if 'board' in data:
      raise PermissionDenied("Changing the board of a ticket is not allowed.")


    if 'status' in data:
        internal_status = VALID_STATUS.get(data['status'])
        if not internal_status:
            raise ValidationError(f"Invalid status '{data['status']}'.")
        update_fields['status'] = internal_status


    if 'priority' in data:
        if data['priority'] not in VALID_PRIORITIES:
            raise ValidationError(f"Invalid priority '{data['priority']}'.")
        update_fields['priority'] = data['priority']

    for field in ['title', 'description', 'due_date']:
        if field in data:
            update_fields[field] = data[field]


    for field, model_field in [('assignee_id', 'assignee'), ('reviewer_id', 'reviewer')]:
        if field in data:
            if data[field] is None:
                update_fields[model_field] = None
            else:
                try:
                    user = User.objects.get(id=data[field])
                    if user not in ticket.board.members.all():
                        raise PermissionDenied(f"{model_field.capitalize()} must be a board member.")
                    update_fields[model_field] = user
                except User.DoesNotExist:
                    raise ValidationError(f"{model_field.capitalize()} not found.")


    for field, value in update_fields.items():
        setattr(ticket, field, value)
    ticket.save()

    return ticket


def delete_ticket_if_permitted(ticket_queryset, pk, request_user):
    try:
        ticket = ticket_queryset.get(pk=pk)
    except Ticket.DoesNotExist:

        raise PermissionDenied("Ticket not found or no permission.")

    if ticket.board.owner != request_user and getattr(ticket, 'created_by', None) != request_user:
        raise PermissionDenied("You do not have permission to delete this ticket.")

    ticket.delete()
from ...models import Ticket

def get_assigned_tickets(user):
    return Ticket.objects.filter(assignee=user)
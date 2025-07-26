from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .serializers import BoardSerializer, BoardDetailSerializer, BoardPatchSerializer, TaskDetailSerializer, CommentSerializer, TaskCommentSerializer
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
from ..models import Board, Ticket, Comment
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth import get_user_model
from rest_framework import status
from django.shortcuts import get_object_or_404

from .services.board_service import  (
    get_board_or_403,
    delete_board_if_owner,
    update_board_members,
    create_board
)
from .services.ticket_service import get_assigned_tickets


class BoardViews(APIView):
    permission_classes = [IsAuthenticated]  
    serializer_class = BoardSerializer

    def get(self, request):
        user = request.user

        boards = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        try:
            board = create_board(request.data, request.user)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BoardSerializer(board)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class BoardDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all().prefetch_related('members', 'tickets')
    permission_classes = [IsAuthenticated]  
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BoardDetailSerializer
        return BoardPatchSerializer

    def get(self, request, pk):
        try:
            board = get_board_or_403(pk, request.user)
            serializer = self.get_serializer(board)
            return Response(serializer.data)
        except (ValidationError, PermissionDenied) as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request, pk):
        return self.update(request, pk)

    def delete(self, request, pk):
        board = self.get_object()
        try:
            delete_board_if_owner(board, request.user)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        board = self.get_object()
        update_board_members(board, self.request.data.get("members"), self.request.user)
        serializer.save()

        

class AssignedTicketsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDetailSerializer


    def get(self, request):
        tickets = get_assigned_tickets(request.user)
        serializer = self.serializer_class(tickets, many=True)
        return Response(serializer.data)
    
class RewieverView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDetailSerializer


    def get(self, request):
        user = request.user
        tickets = Ticket.objects.filter(reviewer=user)
        serializer = TaskDetailSerializer(tickets, many=True)
        return Response(serializer.data)



class TaskCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        tickets = Ticket.objects.filter(reviewer=user)
        serializer = TaskDetailSerializer(tickets, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        User = get_user_model()


        board_id = data.get('board')
        title = data.get('title')
        description = data.get('description')
        status_value = data.get('status')
        priority_value = data.get('priority')
        assignee_id = data.get('assignee_id')
        reviewer_id = data.get('reviewer_id')
        due_date = data.get('due_date')

        if not board_id or not title or not status_value or not priority_value:
            return Response({"error": "board, title, status, and priority are required."}, status=400)


        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return Response({"error": "Board not found."}, status=404)

        if request.user not in board.members.all() and request.user != board.owner:
            return Response({"error": "You are not a member of this board."}, status=403)


        VALID_STATUS = {
            "to-do": "to_do",
            "in-progress": "in_progress",
            "review": "review",
            "done": "done"
        }

        internal_status = VALID_STATUS.get(status_value)
        if not internal_status:
            return Response({"error": f"Invalid status '{status_value}'."}, status=400)


        if priority_value not in ['low', 'medium', 'high']:
            return Response({"error": f"Invalid priority '{priority_value}'."}, status=400)


        assignee = reviewer = None
        if assignee_id:
            try:
                assignee = User.objects.get(id=assignee_id)
                if assignee not in board.members.all():
                    return Response({"error": "Assignee must be a member of the board."}, status=403)
            except User.DoesNotExist:
                return Response({"error": "Assignee not found."}, status=404)

        if reviewer_id:
            try:
                reviewer = User.objects.get(id=reviewer_id)
                if reviewer not in board.members.all():
                    return Response({"error": "Reviewer must be a member of the board."}, status=403)
            except User.DoesNotExist:
                return Response({"error": "Reviewer not found."}, status=404)


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

        serializer = TaskDetailSerializer(ticket)
        return Response(serializer.data, status=201)
    

class TaskDetailView(APIView):
    queryset = Ticket.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user
        return Ticket.objects.filter(
            Q(board__members=user) | Q(board__owner=user)
        )
    
    def post(self, request, pk):
        data = request.data
        User = get_user_model()


        board_id = data.get('board')
        title = data.get('title')
        description = data.get('description')
        status_value = data.get('status')
        priority_value = data.get('priority')
        assignee_id = data.get('assignee_id')
        reviewer_id = data.get('reviewer_id')
        due_date = data.get('due_date')

        if not board_id or not title or not status_value or not priority_value:
            return Response({"error": "board, title, status, and priority are required."}, status=400)


        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return Response({"error": "Board not found."}, status=404)

        if request.user not in board.members.all() and request.user != board.owner:
            return Response({"error": "You are not a member of this board."}, status=403)


        VALID_STATUS = {
            "to-do": "to_do",
            "in-progress": "in_progress",
            "review": "review",
            "done": "done"
        }

        internal_status = VALID_STATUS.get(status_value)
        if not internal_status:
            return Response({"error": f"Invalid status '{status_value}'."}, status=400)


        if priority_value not in ['low', 'medium', 'high']:
            return Response({"error": f"Invalid priority '{priority_value}'."}, status=400)


        assignee = reviewer = None
        if assignee_id:
            try:
                assignee = User.objects.get(id=assignee_id)
                if assignee not in board.members.all():
                    return Response({"error": "Assignee must be a member of the board."}, status=403)
            except User.DoesNotExist:
                return Response({"error": "Assignee not found."}, status=404)

        if reviewer_id:
            try:
                reviewer = User.objects.get(id=reviewer_id)
                if reviewer not in board.members.all():
                    return Response({"error": "Reviewer must be a member of the board."}, status=403)
            except User.DoesNotExist:
                return Response({"error": "Reviewer not found."}, status=404)


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

        serializer = TaskDetailSerializer(ticket)
        return Response(serializer.data, status=201)
    
    def patch(self, request, pk):
        User = get_user_model()
        """Aktualisiert ein bestehendes Ticket"""
        try:
            ticket = self.get_queryset().get(pk=pk)
        except Ticket.DoesNotExist:
            return Response(
                {"error": "Ticket not found or no permission."},
                status=status.HTTP_404_NOT_FOUND
            )

        data = request.data
        update_fields = {}


        if 'board' in data:
            try:
                new_board = Board.objects.get(id=data['board'])
                if request.user not in new_board.members.all() and request.user != new_board.owner:
                    return Response(
                        {"error": "No permission for target board."},
                        status=status.HTTP_403_FORBIDDEN
                    )
                update_fields['board'] = new_board
            except Board.DoesNotExist:
                return Response(
                    {"error": "Board not found."},
                    status=status.HTTP_404_NOT_FOUND
                )


        if 'status' in data:
            status_mapping = {
                "to-do": "to_do",
                "in-progress": "in_progress",
                "review": "review",
                "done": "done"
            }
            internal_status = status_mapping.get(data['status'])
            if not internal_status:
                return Response(
                    {"error": f"Invalid status '{data['status']}'."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            update_fields['status'] = internal_status

      
        if 'priority' in data:
            if data['priority'] not in ['low', 'medium', 'high']:
                return Response(
                    {"error": f"Invalid priority '{data['priority']}'."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            update_fields['priority'] = data['priority']


        for field in ['title', 'description', 'due_date']:
            if field in data:
                update_fields[field] = data[field]


        for field, model_field in [('assignee_id', 'assignee'), ('reviewer_id', 'reviewer')]:
            if field in data:
                try:
                    if data[field] is None:
                        update_fields[model_field] = None
                    else:
                        user = User.objects.get(id=data[field])
                        if user not in ticket.board.members.all():
                            return Response(
                                {"error": f"{field.split('_')[0]} must be a board member."},
                                status=status.HTTP_403_FORBIDDEN
                            )
                        update_fields[model_field] = user
                except User.DoesNotExist:
                    return Response(
                        {"error": f"{field.split('_')[0]} not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )


        for field, value in update_fields.items():
            setattr(ticket, field, value)
        ticket.save()

        serializer = TaskDetailSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def delete(self, request, pk):
        try:
            ticket = self.get_queryset().get(pk=pk)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        board = ticket.board

        if user != board.owner and user not in board.members.all():
            return Response({"error": "You do not have permission to delete this ticket."}, status=status.HTTP_403_FORBIDDEN)

        ticket.delete()
        return Response({"message": f"Ticket {pk} deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    


class TaskCommentsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        try:
            ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return Response(
                {"error": "Task not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        

        board = ticket.board
        user = request.user
        if user != board.owner and user not in board.members.all():
            return Response(
                {"error": "You are not a member of this board."},
                status=status.HTTP_403_FORBIDDEN
            )
        

        comments = Comment.objects.filter(ticket=ticket).order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TaskCommentsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskCommentSerializer
    
    def get(self, request, task_id):
        try:

            ticket = Ticket.objects.get(pk=task_id)
        except Ticket.DoesNotExist:
            return Response(
                {"error": "Task not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
      
        board = ticket.board
        user = request.user
        if user != board.owner and user not in board.members.all():
            return Response(
                {"error": "You are not a member of this board."},
                status=status.HTTP_403_FORBIDDEN
            )
        
   
        comments = Comment.objects.filter(ticket=ticket).order_by('created_at')
        serializer = TaskCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def post(self, request, task_id):  
        user = request.user
        
        try:
            ticket = Ticket.objects.get(pk=task_id)
        except Ticket.DoesNotExist:
            return Response(
                {"error": "Task not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
  
        board = ticket.board
        if user != board.owner and user not in board.members.all():
            return Response(
                {"error": "You are not a member of this board."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = request.data
        content = data.get('content')
        
        if not content:
            return Response(
                {"error": "Content is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
       
        comment = Comment.objects.create(
            ticket=ticket,
            author=user,
            content=content
        )
        
        
        ticket.comments_count = Comment.objects.filter(ticket=ticket).count()
        ticket.save()
        
        serializer = self.serializer_class(comment)
        print(serializer.data)
       
   
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, **kwargs):  
        try:
            task_id = kwargs.get('task_id')
            comment_id = kwargs.get('comment_id')
            
          
            print(f"Lösche Kommentar {comment_id} für Task {task_id}")
            

            comment = get_object_or_404(
                Comment,
                pk=comment_id,
                ticket_id=task_id
            )
            

            if request.user != comment.author and request.user != comment.ticket.board.owner:
                return Response(
                    {"error": "Keine Berechtigung zum Löschen"},
                    status=status.HTTP_403_FORBIDDEN
                )
            

            comment.delete()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            print(f"Fehler beim Löschen: {str(e)}")
            return Response(
                {"error": "Interner Serverfehler"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    

    

    


    


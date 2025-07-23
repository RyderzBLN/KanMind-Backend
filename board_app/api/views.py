from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .serializers import BoardSerializer, BoardDetailSerializer, BoardPatchSerializer, TaskDetailSerializer
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
from ..models import Board, Ticket
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework import status

class BoardViews(APIView):
    permission_classes = [IsAuthenticated]  
    serializer_class = BoardSerializer

    def get(self, request):
        user = request.user

        boards = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)
    
    


    def post(self, request):
        user = request.user
        data = request.data
        
        title = data.get('title')
        members_ids = data.get('members', [])

        if not title:
            return Response({"error": "Title is required."}, status=status.HTTP_400_BAD_REQUEST)
        board = Board.objects.create(title=title, owner=user)

        
        User = get_user_model()
        valid_members = User.objects.filter(id__in=members_ids)

        
        if user not in valid_members:
            board.members.add(user)
        board.members.add(*valid_members)
        board.save()       
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
        serializer_class = self.get_serializer_class()
        try:

            board = self.get_queryset().get(pk=pk)
            

            if board.owner != request.user and request.user not in board.members.all():
                return Response(
                    {"error": "No permission to view this board."},
                    status=status.HTTP_403_FORBIDDEN
                )
            

            serializer = self.get_serializer(board)
            return Response(serializer.data)
            
        except Board.DoesNotExist:
            return Response(
                {"error": "Board not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
    def post(self, request, pk):
        return self.update(request, pk)
    
    def delete(self, request, pk):
        board = self.get_object()
        if board.owner != request.user:
            return Response(
                {"detail": "You do not have permission to delete this board."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        else:
            board.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        user = self.request.user
        board = self.get_object()
        
       
        if board.owner != user:
            raise PermissionDenied("Only the board owner can update this board.")
        
    
        members_ids = self.request.data.get('members')
        if members_ids is not None:
            User = get_user_model()
            valid_members = User.objects.filter(id__in=members_ids)
            board.members.clear()
            board.members.add(*valid_members)
            if user not in valid_members:
                board.members.add(user)  
        
        serializer.save()

        

class AssignedTicketsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDetailSerializer


    def get(self, request):
        user = request.user
        tickets = Ticket.objects.filter(assignee=user)
        serializer = TaskDetailSerializer(tickets, many=True)
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
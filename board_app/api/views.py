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
from .services.ticket_service import (
    get_assigned_tickets,
    get_reviewed_tickets,
    create_ticket_from_data,
    update_ticket_from_data,
    delete_ticket_if_permitted
)

from .services.comment_service import (
    get_ticket_comments,
    create_ticket_comment,
    delete_comment
)


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
        tickets = get_reviewed_tickets(request.user)
        serializer = TaskDetailSerializer(tickets, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            ticket = create_ticket_from_data(request.data, request.user)
            serializer = TaskDetailSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
    

class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDetailSerializer
      
    def get_queryset(self):
        user = self.request.user
        return Ticket.objects.filter(board__members=user) | Ticket.objects.filter(board__owner=user)

    def patch(self, request, pk):
        try:
            ticket = self.get_queryset().get(pk=pk)
            updated_ticket = update_ticket_from_data(ticket, request.data, request.user)
            serializer = self.serializer_class(updated_ticket)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found or no permission."}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
    def delete(self, request, pk):
        try:
            delete_ticket_if_permitted(self.get_queryset(), pk, request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)




class TaskCommentsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskCommentSerializer

    def get(self, request, task_id):
        try:
            comments = get_ticket_comments(task_id, request.user)
            serializer = self.serializer_class(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request, task_id):
        content = request.data.get("content")
        if not content:
            return Response({"error": "Content is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            comment = create_ticket_comment(task_id, request.user, content)
            serializer = self.serializer_class(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Ticket.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
    

class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, **kwargs):
        try:
            task_id = kwargs.get('task_id')
            comment_id = kwargs.get('comment_id')

            delete_comment(task_id, comment_id, request.user)

            return Response(status=status.HTTP_204_NO_CONTENT)

        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response(
                {"error": "Interner Serverfehler"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    

    

    


    


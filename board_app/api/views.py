from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .serializers import BoardSerializer, BoardDetailSerializer, BoardPatchSerializer
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
from ..models import Board as Board
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

        




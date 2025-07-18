from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .serializers import BoardSerializer
from ..models import Board as Board
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework import status

class BoardViews(APIView):
    permission_classes = [IsAuthenticated]  # Nur eingeloggt erlaubt
    serializer_class = BoardSerializer

    def get(self, request):
        user = request.user
        # Boards filtern: Entweder Eigentümer oder Mitglied
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










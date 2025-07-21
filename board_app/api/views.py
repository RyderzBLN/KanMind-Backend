from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
<<<<<<< HEAD
from .serializers import BoardSerializer, BoardDetailSerializer, BoardMembersUpdateSerializer, BoardUpdateSerializer
from rest_framework.generics import RetrieveAPIView
=======
from .serializers import BoardSerializer
>>>>>>> parent of 57cd40b (add GET /api/boards/{board_id}/)
from ..models import Board as Board
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveUpdateAPIView

class BoardViews(APIView):
    permission_classes = [IsAuthenticated]
    
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
        serializer = BoardSerializer(board)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BoardUpdateView(UpdateAPIView):
    queryset = Board.objects.all().prefetch_related('members', 'owner')
    serializer_class = BoardUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        board = self.get_object()
        user = self.request.user
        
        # Strikte Berechtigungsprüfung
        if user != board.owner and user not in board.members.all():
            raise PermissionDenied(
                {"detail": "Nur Besitzer oder Mitglieder dürfen Änderungen vornehmen"},
                code=status.HTTP_403_FORBIDDEN
            )
        
        validated_data = serializer.validated_data
        
        # Titel aktualisieren
        if 'title' in validated_data:
            board.title = validated_data['title']
        
        # Mitglieder aktualisieren
        if 'members' in validated_data:
            new_member_ids = validated_data['members']
            
            # Owner immer als Mitglied behalten
            if board.owner.id not in new_member_ids:
                new_member_ids.append(board.owner.id)
            
            # Existierende Mitglieder abrufen
            current_member_ids = set(board.members.values_list('id', flat=True))
            new_member_ids_set = set(new_member_ids)
            
            # Änderungen berechnen
            to_remove = current_member_ids - new_member_ids_set
            to_add = new_member_ids_set - current_member_ids
            
            # Änderungen anwenden
            board.members.remove(*to_remove)
            board.members.add(*to_add)
        
        board.save()#




<<<<<<< HEAD
class BoardDetailView(RetrieveUpdateAPIView):
    queryset = Board.objects.all().prefetch_related('members', 'tickets')
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated]  # Nur eingeloggt erlaubt
=======
>>>>>>> parent of 57cd40b (add GET /api/boards/{board_id}/)


class BoardMembersUpdateView(UpdateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardMembersUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        board = self.get_object()
        user = self.request.user

        # Berechtigung prüfen
        if user != board.owner and user not in board.members.all():
         raise PermissionDenied(
        "Nur der Besitzer oder Mitglieder dürfen Mitglieder verwalten"
    )

        # Mitglieder komplett ersetzen
        new_members = serializer.validated_data['members']
        board.members.set(new_members)


#class BoardUpdateView(UpdateAPIView):
 #   queryset = Board.objects.all().prefetch_related('members', 'owner')
  #  serializer_class = BoardUpdateSerializer
  #  permission_classes = [IsAuthenticated]
#
  #  def perform_update(self, serializer):
   #     board = self.get_object()
   #     user = self.request.user
   #     
   #     # Strikte Berechtigungsprüfung
   #     if user != board.owner and user not in board.members.all():
   #         raise PermissionDenied(
   #             {"detail": "Nur Besitzer oder Mitglieder dürfen Änderungen vornehmen"},
   #             code=status.HTTP_403_FORBIDDEN
   #         )
   #     
  #      # Mitglieder-Update erzwingen
    #    if 'members' in serializer.validated_data:
    #        new_members = serializer.validated_data['members']
    #        if board.owner.id not in new_members:
    #            new_members.append(board.owner.id)
     #       board.members.clear()  # Alle bestehenden entfernen
    #        board.members.add(*new_members)  # Neue hinzufügen
        
        # Titel aktualisieren falls vorhanden
        if 'title' in serializer.validated_data:
            board.title = serializer.validated_data['title']
        
        board.save()
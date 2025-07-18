from rest_framework import serializers
from ..models import Board
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.response import Response




class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id')

    class Meta:
        model = Board
        fields = ['id', 'title',  'member_count', 'ticket_count', "tasks_high_prio_count", "tasks_to_do_count" , 'owner_id']

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tickets.count()
    
    def get_tasks_to_do_count(self, obj):
        return obj.tickets.filter(status='to_do').count()
    
    def get_tasks_high_prio_count(self, obj):
        return obj.tickets.filter(priority='high').count()
    

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
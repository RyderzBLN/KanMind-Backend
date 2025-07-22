from rest_framework import serializers
from ..models import Board, Ticket
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.response import Response



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', "fullname"]



class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'description', 'status', 'priority', "assignee", "reviewer", 'due_date', 'comments_count']




class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id')
   # members = UserSerializer(many=True, read_only=True)
   # tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title',  'member_count', 'ticket_count',  "tasks_to_do_count" , "tasks_high_prio_count", 'owner_id']

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tickets.count()
    
    def get_tasks_to_do_count(self, obj):
        return obj.tickets.filter(status='to_do').count()
    
    def get_tasks_high_prio_count(self, obj):
        return obj.tickets.filter(priority='high').count()
    


class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source='owner.id')
    members = UserSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

    def get_tasks(self, obj):
        tickets = obj.tickets.all().select_related('assignee', 'reviewer')
        return TaskDetailSerializer(tickets, many=True).data
    
    def delete(self, request, pk):
        board = self.get_object()
        if board.owner != request.user:
            return Response(
                {"detail": "You do not have permission to delete this board."},
                status=status.HTTP_403_FORBIDDEN
            )
        else:
            board.delete()
        
    

class BoardPatchSerializer(serializers.ModelSerializer):
    owner_data = UserSerializer(source='owner', read_only=True)
    members_data = UserSerializer(source='members', many=True, read_only=True)
    
    # Für die Eingabe (POST/PUT/PATCH): Mitglieder-IDs unter members
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=get_user_model().objects.all(),
        write_only=True,
        required=False
    )
    
   

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data', 'members']

    def get_tasks(self, obj):
        tickets = obj.tickets.all().select_related('assignee', 'reviewer')
        return TaskDetailSerializer(tickets, many=True).data
    

class TaskDetailSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    status = serializers.CharField(source='get_status_display')
    priority = serializers.CharField(source='get_priority_display')
    comments_count = serializers.IntegerField(default=0)

    class Meta:
        model = Ticket
        fields = [
            'id', 
            'title', 
            'description', 
            'status', 
            'priority', 
            'assignee', 
            'reviewer', 
            'due_date', 
            'comments_count'
        ]

   # def create(self, validated_data):
   #     members_data = validated_data.pop('members', [])
   #     board = Board.objects.create(**validated_data)
   #     for member_data in members_data:
   #         user = get_user_model().objects.get(id=member_data['id'])
   #         board.members.add(user)
   #     return board
  #
  #  def update(self, instance, validated_data):
  #      instance.title = validated_data.get('title', instance.title)
  #      instance.save()
  #      return instance

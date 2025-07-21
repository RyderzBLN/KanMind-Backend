from rest_framework import serializers
from ..models import Board
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.response import Response



<<<<<<< HEAD
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'fullname']


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'description', 'status', 'priority', "assignee", "reviewer", 'due_date', 'comments_count']



=======
>>>>>>> parent of 57cd40b (add GET /api/boards/{board_id}/)

class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id')

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
    

<<<<<<< HEAD

class BoardDetailSerializer(serializers.ModelSerializer):
    owner_data = UserSerializer(source='owner', read_only=True)
    members_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data']
        extra_kwargs = {
            'title': {'required': False}
        }

    def get_members_data(self, obj):
        members = obj.members.all()
        return UserSerializer(members, many=True).data

    def update(self, instance, validated_data):
        # Manuelles Update für einfache Felder
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        
        # Mitglieder separat aktualisieren
        if 'members' in self.initial_data:
            members_ids = self.initial_data['members']
            instance.members.set(members_ids)
        
        return instance

class BoardMembersUpdateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Board
        fields = ['members']  # Nur Mitglieder, kein Titel!
        read_only_fields = ['id']

    def validate_members(self, value):
        # Validiert, dass alle Mitglieder-IDs existieren
        User = get_user_model()
        existing_users = User.objects.filter(id__in=value)
        if len(existing_users) != len(value):
            raise serializers.ValidationError("Ungültige Benutzer-IDs")
        return value


class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    owner_data = UserSerializer(source='owner', read_only=True)
    members_data = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'owner_data', 'members_data']
        extra_kwargs = {'title': {'required': False}}

    def get_members_data(self, obj):
        return UserSerializer(obj.members.all(), many=True).data

    def validate_members(self, value):
        if value is not None:
            User = get_user_model()
            existing_users = User.objects.filter(id__in=value)
            if len(existing_users) != len(value):
                existing_ids = set(existing_users.values_list('id', flat=True))
                invalid_ids = [id for id in value if id not in existing_ids]
                raise serializers.ValidationError(f"Ungültige Benutzer-IDs: {invalid_ids}")
        return value
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


class BoardDetailResponseSerializer(serializers.ModelSerializer):
    owner_data = UserSerializer(source='owner', read_only=True)
    members_data = UserSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data']
        read_only_fields = fields  # Alle Felder sind read-only
=======
>>>>>>> parent of 57cd40b (add GET /api/boards/{board_id}/)

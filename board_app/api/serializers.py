from rest_framework import serializers
from ..models import Board


class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id')

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'member_count', 'ticket_count', "tasks_high_prio_count", "tasks_to_do_count"]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tickets.count()
    
    def get_tasks_to_do_count(self, obj):
        return obj.tickets.filter(status='to_do').count()
    
    def get_tasks_high_prio_count(self, obj):
        return obj.tickets.filter(priority='high').count()
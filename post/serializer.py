from rest_framework import serializers
from .models import Application,Opportunity,Team


class team_serializer(serializers.ModelSerializer):
    class Meta :
        model = Team
        fields = [
            'id',
            'name',
        ]

class application_serializer(serializers.ModelSerializer):
    class Meta :
        model = Application
        fields = [
            'id',
            'proposal',
            'status',
            'approve',
        ]

class opportunity_serializer(serializers.ModelSerializer):
    class Meta :
        model = Opportunity
        fields = [
            'id',
            'title',
            'description',
            'status',
            'Type',
            'category',
            'skills',
        ]

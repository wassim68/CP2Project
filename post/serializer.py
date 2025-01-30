from rest_framework import serializers
from .models import Application,Opportunity,Team
from Auth.serlaizers import UserStudentSerializer

class team_serializer(serializers.ModelSerializer):
    #students = UserStudentSerializer(required = False,many=True)
    class Meta :
        model = Team
        fields = [
            'id',
            'name',
            'students',
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

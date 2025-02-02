from rest_framework import serializers
from .models import Application,Opportunity,Team
from Auth.serlaizers import UserStudentSerializer,SkillsSerializer

class team_serializer(serializers.ModelSerializer):
    #students = UserStudentSerializer(required = False,many=True)
    class Meta :
        model = Team
        fields = [
            'id',
            'name',
            'students',
            'leader'
        ]

class application_serializer(serializers.ModelSerializer):
    status=serializers.CharField(read_only=True)
    class Meta :
        model = Application
        fields = [
            'id',
            'proposal',
            'status',
            'approve',
        ]

class opportunity_serializer(serializers.ModelSerializer):
    skills=SkillsSerializer(many=True)
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['skills'] = [skill['name'] for skill in representation['skills']]
        return representation
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
        

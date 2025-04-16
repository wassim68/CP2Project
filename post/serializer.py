from rest_framework import serializers
from .models import Opportunity,Team
from Auth.serlaizers import UserStudentSerializer,SkillsSerializer,UserCompanySerializer
from Auth.models import Skills

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

class opportunity_serializer(serializers.ModelSerializer):
    company=UserCompanySerializer(required=False)
    skill_input = serializers.ListField(
      child=serializers.CharField(),
      required=False,
      write_only=1)
    skills=SkillsSerializer(many=True,read_only=True)
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['skills'] = [skill['name'] for skill in representation['skills']]
        return representation
    def create(self, validated_data):
        skill_names = validated_data.pop('skill_input',[])
        student = Opportunity.objects.create(**validated_data)
        skills = Skills.objects.filter(name__in=skill_names)  
        student.skills.set(skills)  
        return student
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
            'endday',
            'skill_input',
            'worktype',
            'company',
            'created_at',
            'duration'
        ]
        

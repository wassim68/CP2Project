from rest_framework import serializers
from .models import Opportunity,Team,TeamInvite
from Auth.serlaizers import UserStudentSerializer,SkillsSerializer,UserCompanySerializer,StudentSerializer
from Auth.models import Skills,User

class team_serializer(serializers.ModelSerializer):
    # Write-only: accept student and leader IDs
    student_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True
    )
    leader_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )

    # Read-only: return full user objects
    students = UserStudentSerializer(many=True, read_only=True)
    leader = UserStudentSerializer(read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'student_ids', 'students', 'leader_id', 'leader', 'createdate','category','description']

    def create(self, validated_data):
        student_ids = validated_data.pop('student_ids', [])
        leader = validated_data.pop('leader_id')
        team = Team.objects.create(leader=leader, **validated_data)
        team.students.set(student_ids)
        return team

    def update(self, instance, validated_data):
        student_ids = validated_data.pop('student_ids', None)
        leader = validated_data.pop('leader_id', None)
        instance = super().update(instance, validated_data)
        if student_ids is not None:
            instance.students.set(student_ids)
        if leader is not None:
            instance.leader = leader
            instance.save()
        return instance

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
        
class TeamInviteSerializer(serializers.ModelSerializer):

    team_id = serializers.PrimaryKeyRelatedField(
        many=False, queryset=Team.objects.all(),write_only=True
    )

    inviter_id = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all(),write_only=True
    )

    receiver_id = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all(),write_only=True
    )

    team = team_serializer
    inviter = UserCompanySerializer
    receiver = UserCompanySerializer 

    class Meta :
        model = TeamInvite
        fields= [
            'id',
            'inviter',
            'inviter_id',
            'receiver',
            'receiver_id',
            'team',
            'team_id',
            'status',
            'createdate'
        ]
        read_only_fields = ['id','createdate']
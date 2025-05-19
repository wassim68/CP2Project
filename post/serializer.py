from rest_framework import serializers
from .models import Opportunity,Team,TeamInvite
from Auth.serlaizers import UserStudentSerializer,UserCompanySerializer,StudentSerializer
from Auth.models import User,Student

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
    
    skills=serializers.ListField(
      child=serializers.JSONField(),
      required=False,
    )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation
    
    def create(self, validated_data):
        student = Opportunity.objects.create(**validated_data)
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
            'enddate',
            'skill_input',
            'worktype',     
            'company',
            'created_at',
            'startdate',
            'location',
        ]
        
class TeamInviteSerializer(serializers.ModelSerializer):

    team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(), write_only=True
    )
    inviter_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )
    receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )
    team = team_serializer(read_only=True)
    inviter = UserStudentSerializer(read_only=True)
    receiver = UserStudentSerializer(read_only=True)
    class Meta:
        model = TeamInvite
        fields = [
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
        read_only_fields = ['id', 'createdate', 'team', 'inviter', 'receiver']
    def create(self, validated_data):
        team = validated_data.pop('team_id')
        inviter_user = validated_data.pop('inviter_id')
        receiver_user = validated_data.pop('receiver_id')
        inviter = User.objects.get(id=inviter_user.id)
        receiver = User.objects.get(id=receiver_user.id)
        return TeamInvite.objects.create(
            team=team,
            inviter=inviter,
            receiver=receiver,
            **validated_data
            )

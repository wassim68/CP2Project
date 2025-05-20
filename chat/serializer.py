from rest_framework import serializers
from Auth.serlaizers import UserStudentSerializer,UserCompanySerializer,StudentSerializer
from Auth.models import User,Student
from .models import Chat,Message

class MessageSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'receiver',
            'sent_time',
            'seen',
            'message'
        ]

    

class ChatSerializer(serializers.ModelSerializer):

    student_id = serializers.PrimaryKeyRelatedField(
        many=False, queryset=User.objects.all(), write_only=True
    )
    company_id = serializers.PrimaryKeyRelatedField(
        many=False,queryset=User.objects.all(), write_only=True
    )
    last_message = MessageSerializer(many=False, read_only=True, required=False)
    student = UserStudentSerializer(many=False, read_only=True, required=False)
    company = UserCompanySerializer(many=False, read_only=True, required=False)
    room_name = serializers.CharField(read_only=True)
    unseen_count = serializers.SerializerMethodField()
    class Meta:
        model = Chat
        fields = [
            'id',
            'student',
            'student_id',
            'company',
            'company_id',
            'room_name',
            'last_message',
            'unseen_count'
        ]

   
    def get_unseen_count(self,obj):
        user_id = self.context['user_id']
        if user_id is not None:
            return obj.messages.filter(seen=False,receiver=user_id).all().count()
        else :
            return 0

    

    def create(self, validated_data):
        student = validated_data.pop('student_id')
        company = validated_data.pop('company_id')
        chat = Chat.objects.create(student=student,company=company, **validated_data)
        return chat
    

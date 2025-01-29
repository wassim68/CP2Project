from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, company, Skills, Student

class CompanySerializer(serializers.ModelSerializer):
  class Meta:
    model = company
    fields = '__all__'

class SkillsSerializer(serializers.ModelSerializer):
  class Meta:
    model = Skills
    fields = ['name']

class StudentSerializer(serializers.ModelSerializer):
  Skills = SkillsSerializer(many=True, read_only=True)
  class Meta:
    model = Student
    fields = '__all__'

class UserCompanySerializer(serializers.ModelSerializer):
  company = CompanySerializer()
  password=serializers.CharField(write_only=1)
  type=serializers.CharField(read_only=True)
  class Meta:
    model = User
    fields = ['id','name', 'email', 'Number', 'company','type','profilepic','date_joined','password']
  def create(self, validated_data):
        company_data = validated_data.pop('company', None)  
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        if company_data:
            ompany = company.objects.create(**company_data)
            user.company = ompany  
            user.save()

        return user
class UserStudentSerializer(serializers.ModelSerializer):
  Student = StudentSerializer()
  password=serializers.CharField(write_only=1)
  type=serializers.CharField(read_only=True)
  def create(self, validated_data):
        Student_data = validated_data.pop('Student', None)  
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        if Student_data:
            student = Student.objects.create(**Student_data)
            user.Student = student  
            user.save()
        return user
  class Meta:
    model = User
    fields = ['id','name', 'email', 'Number', 'Student','type','profilepic','date_joined','password']
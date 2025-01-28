from rest_framework import serializers
from .models import User, company, Skills, Student

class CompanySerializer(serializers.ModelSerializer):
  class Meta:
    model = company
    fields = ['id','category']

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
  company = CompanySerializer(read_only=True)
  type=serializers.CharField(read_only=True)
  class Meta:
    model = User
    fields = ['id','name', 'email', 'Number', 'company','type']
class UserStudentSerializer(serializers.ModelSerializer):
  Student = StudentSerializer(read_only=True)
  type=serializers.CharField(read_only=True)
  class Meta:
    model = User
    fields = ['id','name', 'email', 'Number', 'Student','type']
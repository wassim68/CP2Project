from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, company, Skills, Student

class CompanySerializer(serializers.ModelSerializer):
  class Meta:
    model = company
    fields = ['category']

class SkillsSerializer(serializers.ModelSerializer):
  class Meta:
    model = Skills
    fields = ['name']

class StudentSerializer(serializers.ModelSerializer):
  skills = SkillsSerializer(many=True, read_only=True)
  class Meta:
    model = Student
    fields = ['education','gendre','skills','rating']
  def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['skills'] = [skill['name'] for skill in representation['skills']]
        return representation

class UserCompanySerializer(serializers.ModelSerializer):
  company = CompanySerializer()
  password=serializers.CharField(write_only=1)
  type=serializers.CharField(read_only=True)
  class Meta:
    model = User
    fields = ['id','name', 'email', 'number', 'company','type','profilepic','date_joined','password']
  def create(self, validated_data):
        company_data = validated_data.pop('company', None)  
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        if company_data:
            ompany = company.objects.create(**company_data)
            user.company = ompany  
            user.save()
        return user
  def to_representation(self, instance):
        representation = super().to_representation(instance)
        company_representation = representation.pop('company')
        representation.update(company_representation)  # Merge company data into the main dictionary
        return representation
class UserStudentSerializer(serializers.ModelSerializer):
  student = StudentSerializer()
  password=serializers.CharField(write_only=1)
  type=serializers.CharField(read_only=True)
  def create(self,validated_data):
        Student_data = validated_data.pop('student', None)  
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        if Student_data:
            student = Student.objects.create(**Student_data)
            user.student = student  
            user.save()
        return user
  def to_representation(self, instance):
        representation = super().to_representation(instance)
        company_representation = representation.pop('student')
        representation.update(company_representation)  
        return representation
  class Meta:
    model = User
    fields = ['id','name', 'email', 'number', 'student','type','profilepic','date_joined','password']
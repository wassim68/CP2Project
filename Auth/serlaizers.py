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
  skill_input = serializers.ListField(
      child=serializers.CharField(),
      required=False,
      write_only=1)
  skills = SkillsSerializer(many=True, required=False)
  class Meta:
    model = Student
    fields = ['education','gendre','skills','rating','category','skill_input']
  def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['skills'] = [skill['name'] for skill in representation['skills']]
        return representation
  def create(self, validated_data):
        skill_names = validated_data.pop('skill_input',[])
        student = Student.objects.create(**validated_data)
        skills = Skills.objects.filter(name__in=skill_names)  
        student.skills.set(skills)  
        return student
  def update(self, instance, validated_data):
        skill_names = validated_data.pop('skill_input',[])
        instance = super().update(instance, validated_data)
        skills = Skills.objects.filter(name__in=skill_names)
        instance.skills.set(skills)
        return instance

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
  def update(self, instance, validated_data):
        company_data = validated_data.pop('company', None)
        instance = super().update(instance, validated_data)
        if company_data is not None:
            company_instance = instance.company
            if company_instance:
                company_serializer = CompanySerializer(
                    instance=company_instance,
                    data=company_data,
                    partial=self.partial  
                )
            company_serializer.is_valid(raise_exception=True)
            company = company_serializer.save()
            instance.company = company
            instance.save()
        return instance
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
            skill_names=Student_data.pop('skill_input',[])
            student = Student.objects.create(**Student_data)
            user.student = student  
            skills = Skills.objects.filter(name__in=skill_names)  
            student.skills.set(skills)  
            user.save()
        return user
  def to_representation(self, instance):
        representation = super().to_representation(instance)
        company_representation = representation.pop('student')
        representation.update(company_representation)  
        return representation
  def update(self, instance, validated_data):
        Student_data = validated_data.pop('student', None)
        instance = super().update(instance, validated_data)
        if Student_data is not None:
            Student_instance = instance.student
            if Student_instance:
                Student_serializer = StudentSerializer(
                    instance=Student_instance,
                    data=Student_data,
                    partial=self.partial  
                )
            Student_serializer.is_valid(raise_exception=True)
            Student = Student_serializer.save()
            instance.student = Student
            instance.save()
        return instance
  class Meta:
    model = User
    fields = ['id','name', 'email', 'number', 'student','type','profilepic','date_joined','password']
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, company, Skills, Student,MCF
from . import tasks
class Fcmserlaizer(serializers.ModelSerializer):
  class Meta:
    model=MCF
    fields=['token']

class CompanySerializer(serializers.ModelSerializer):
  class Meta:
    model = company
    fields = ['category']

class SkillsSerializer(serializers.ModelSerializer):
  class Meta:
    model = Skills
    fields = ['name']
class EducationSerializer(serializers.Serializer):
    degree = serializers.CharField()
    institution = serializers.CharField()
    start = serializers.IntegerField()
    end = serializers.IntegerField()
class StudentSerializer(serializers.ModelSerializer):
  experience=serializers.ListField(
      child=serializers.JSONField()
  )
  skill_input = serializers.ListField(
      child=serializers.CharField(),
      required=False,
      write_only=True)
  skills = SkillsSerializer(many=True, required=False)
  education=serializers.ListField(
      child=EducationSerializer(),
      required=False
  )
  experience=serializers.ListField(
      child=serializers.CharField(),
      required=False
  )
  class Meta:
    model = Student
    fields = ['education','gendre','description','skills','rating','category','skill_input','cv','experience','savedposts']
  def to_representation(self, instance):
    representation = super().to_representation(instance)
    skills = representation.get('skills', [])
    if skills and isinstance(skills[0], dict) and 'name' in skills[0]:
        representation['skills'] = [skill['name'] for skill in skills]

    return representation
  def create(self, validated_data):
        skill_names = validated_data.pop('skill_input',[])
        student = Student.objects.create(**validated_data)
        skills = Skills.objects.filter(name__in=skill_names)
        student.skills.set(skills)  
        return student
  def update(self, instance, validated_data):
        skill_names = validated_data.pop('skill_input',[])
        education=validated_data.pop('education',None)
        if education :
                instance.education+=education
                instance.save()
        instance = super().update(instance, validated_data)
        skills = Skills.objects.filter(name__in=skill_names)
        instance.skills.set(skills)
        return instance


class UserCompanySerializer(serializers.ModelSerializer):
  company = CompanySerializer(required=False)
  password=serializers.CharField(write_only=1)
  type=serializers.CharField(read_only=True)
  location=serializers.CharField(required=False)
  pic=serializers.ImageField(required=False)
  class Meta:
    model = User
    fields = ['id','name', 'email', 'number', 'company','type','pic','profilepic','links','date_joined','password','location']
  def create(self, validated_data):
        company_data = validated_data.pop('company', None)  
        validated_data['password'] = make_password(validated_data['password'])
        if 'pic' in validated_data:
            validated_data['profilepic']= tasks.upload_to_supabase(validated_data.pop('pic'),validated_data['name'])
        user = User.objects.create(**validated_data)
        if company_data:
            ompany = company.objects.create(**company_data)
            user.company = ompany  
            user.save()
        ser=CompanySerializer(data={'skill_input':[]})
        if ser.is_valid():
            ser.save()
        user.company=ser.instance
        user.save()
        return user
  def update(self, instance, validated_data):
        company_data = validated_data.pop('company', None)
        if 'pic' in validated_data:
            validated_data['profilepic']= tasks.upload_to_supabase(validated_data.pop('pic'),instance.name)
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
  student = StudentSerializer(required=False)
  password=serializers.CharField(write_only=1)
  type=serializers.CharField(read_only=True)
  pic=serializers.ImageField(required=False)
  cv_input=serializers.FileField(required=False)
  location=serializers.CharField(required=False)
  def create(self,validated_data):
        Student_data = None
        if 'student' in validated_data:
         Student_data = validated_data.pop('student', None)  
        validated_data['password'] = make_password(validated_data['password'])
        if 'pic' in validated_data:
         validated_data['profilepic']= tasks.upload_to_supabase(validated_data.pop('pic'),validated_data['name'])
        user = User.objects.create(**validated_data)
        if Student_data:
            skill_names=Student_data.pop('skill_input',[])
            student = Student.objects.create(**Student_data)
            user.student = student  
            skills = Skills.objects.filter(name__in=skill_names)  
            student.skills.set(skills)  
            user.save()
        ser=StudentSerializer(data={'skill_input':[]})
        if ser.is_valid():
            ser.save()
        user.student=ser.instance
        user.save()
        return user
  def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'student' in representation:
         company_representation = representation.pop('student')
        representation.update(company_representation)  
        return representation
  def update(self, instance, validated_data):
        Student_data = validated_data.pop('student', {})
        if 'pic' in validated_data:
            validated_data['profilepic']= tasks.upload_to_supabase(validated_data.pop('pic'),instance.name)
        if 'cv_input' in validated_data:
            Student_data['cv']= tasks.upload_to_supabase(validated_data.pop('cv_input'),instance.name)
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
    fields = ['id','name', 'email', 'number', 'student','type','profilepic','pic','cv_input','links','date_joined','password','location']

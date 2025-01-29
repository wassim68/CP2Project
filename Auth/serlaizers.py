from rest_framework import serializers
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
  type=serializers.CharField(read_only=True)
  class Meta:
    model = User
    fields = ['id','name', 'email', 'Number', 'company','type']
  def create(self, validated_data):
        company_data = validated_data.pop('company', None)  
        user = User.objects.create(**validated_data)
        if company_data:
            ompany = company.objects.create(**company_data)
            user.company = ompany  
            user.save()

        return user
class UserStudentSerializer(serializers.ModelSerializer):
  Student = StudentSerializer()
  type=serializers.CharField(read_only=True)
  class Meta:
    model = User
    fields = ['id','name', 'email', 'Number', 'Student','type']
from django.db import models
from django.contrib.auth.models import  AbstractUser,BaseUserManager,PermissionsMixin
from post.models import application,opportunity,team

types = {}
categories = {}
skills_list = {}


class company(models.Model):
    category = models.CharField(choices= categories)
    opportunities = models.models.ForeignKey(opportunity, on_delete=models.CASCADE,related_name = 'opportunies')

class student(models.Model):
    skills = models.CharField(choices= skills_list)
    rating = models.IntegerField(default=0)
    applications = models.ForeignKey(application,on_delete= models.CASCADE,related_name='applications')
    

class user(AbstractUser,PermissionsMixin):
    email = models.email_field()
    number = models.models.IntegerField()
    created_date = models.DateField(auto_now_add=True)
    profile_pic = models.ImageField(null = 1)
    Type = models.CharField( choices= types)
    companyID = models.OneToOneField(company , on_delete= models.CASCADE,related_name="company", null = 1)
    studentID = models.OneToOneField(student , on_delete= models.CASCADE,related_name="student", null = 1)


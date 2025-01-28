from django.db import models
from Auth.models import student,company


types = {}
categories = {}
skills = {}
opp_status = {}
app_status = {}

class application(models.Model):
    proposal = models.TextField()
    status = models.CharField(choices= app_status)
    approve = models.BooleanField(default= 0)
    team = models.OneToOneField(team,related_name= 'team')
    student = models.OneToOneField(student , related_name='student')


class opportunity(models.Model):
    title = models.TextField()
    description = models.TextField()
    Type = models.CharField(choices= types)
    category = models.CharField(choices= categories)
    skills = models.CharField(choices= skills)
    status = models.CharField(choices=opp_status)
    applications = models.ForeignKey(application,related_name= 'applications')


class team(models.Model):
    name = models.TextField()
    students = models.ForeignKey(student,related_name='students')
    applications = models.ForeignKey(application,related_name='applications')

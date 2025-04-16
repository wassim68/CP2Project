from django.db import models
from Auth.models import Student,Skills,company,User,CATEGORY_CHOICES
from application.models import Application
TYPES = [
    ('internship', 'Internship'),
    ('Problem', 'Problem'),
]

OPPORTUNITY_STATUS = [
    ('open', 'Open'),
    ('closed', 'Closed'),
]

work_type=[
    ('Online', 'Online'),
    ('Onsite', 'Onsite'),
    ('Hybrid', 'Hybrid'),
]
class Opportunity(models.Model):
    worktype=models.CharField(choices=work_type, max_length=20,default='Onsite')
    company = models.ForeignKey(User,related_name='opportunity',on_delete=models.CASCADE,null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    Type = models.CharField(choices=TYPES, max_length=20,)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=30)
    skills = models.ManyToManyField(Skills, verbose_name=("Skills"))
    status = models.CharField(choices=OPPORTUNITY_STATUS, max_length=15,default='open')
    applications = models.ManyToManyField(Application, related_name='opportunities')
    endday= models.DateField(null=True)
    duration=models.IntegerField(null=True)
    created_at=models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.title

class Team(models.Model):
    name = models.CharField(max_length=255)
    students = models.ManyToManyField(User, related_name='teams')
    leader = models.ForeignKey(User, related_name='owned_teams', on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.name

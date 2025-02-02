from django.db import models
from Auth.models import Student,Skills,company,User,CATEGORY_CHOICES
TYPES = [
    ('internship', 'Internship'),
    ('Problem', 'Problem'),
]

OPPORTUNITY_STATUS = [
    ('open', 'Open'),
    ('closed', 'Closed'),
    ('pending', 'Pending'),
]

APPLICATION_STATUS = [
    ('submitted', 'Submitted'),
    ('under_review', 'Under Review'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]

class Application(models.Model):
    proposal = models.TextField()
    status = models.CharField(choices=APPLICATION_STATUS, max_length=20,default='submitted')
    approve = models.BooleanField(default=False)
    team = models.ForeignKey('Team', related_name='applications', on_delete=models.CASCADE,null=1)
    student = models.ForeignKey(User, related_name='applications', on_delete=models.CASCADE,null=1)

    def __str__(self):
        return f"Application by {self.student} - Status: {self.status}"

class Opportunity(models.Model):
    company = models.ForeignKey(User,related_name='opportunity',on_delete=models.CASCADE,null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    Type = models.CharField(choices=TYPES, max_length=20)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=30)
    skills = models.ManyToManyField(Skills, verbose_name=("Skills"))
    status = models.CharField(choices=OPPORTUNITY_STATUS, max_length=15)
    applications = models.ManyToManyField(Application, related_name='opportunities')

    def __str__(self):
        return self.title

class Team(models.Model):
    name = models.CharField(max_length=255)
    students = models.ManyToManyField(User, related_name='teams',null= True)
    leader = models.ForeignKey(User, related_name='owned_teams', on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.name

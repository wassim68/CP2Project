from django.db import models
from Auth.models import Student,Skills,company,User,CATEGORY_CHOICES
from application.models import Application
from Auth.models import Student

TYPES = [
    ('internship', 'Internship'),
    ('Problem', 'Problem'),
]

INVITE_STATUS = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]

OPPORTUNITY_STATUS = [
    ('open', 'Open'),
    ('closed', 'Closed'),
]
TEAM_CATEGORY = [
    ('project', 'project'),
    ('study', 'study'),
    ('research', 'research'),
    ('hackathon', 'hackathon'),
    ('others', 'others'),
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
    enddate= models.DateField(null=True)
    startdate=models.DateField(null=1)

    created_at=models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.title

class Team(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True)
    #skills = models.ManyToManyField(Skills, verbose_name=("Skills"),related_name='teams')
    category = models.CharField(choices=TEAM_CATEGORY, max_length=20,default='others')
    students = models.ManyToManyField(User, related_name='teams')
    leader = models.ForeignKey(User, related_name='owned_teams', on_delete=models.DO_NOTHING,null=True)
    createdate = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.name
    
class TeamInvite(models.Model):
    createdate = models.DateTimeField(auto_now_add=True,null=True)
    inviter = models.ForeignKey(User, verbose_name=("inviter"),blank=True, null=True,on_delete=models.SET_NULL,related_name="sent_invites")  
    receiver = models.ForeignKey(User, verbose_name=("receiver"),blank=True, null=True,on_delete=models.SET_NULL,related_name="pending_invites")   
    status = models.CharField(choices=INVITE_STATUS,max_length=8,default='pending')
    team = models.ForeignKey(Team,verbose_name="Team",null=False,on_delete=models.CASCADE,related_name="invites")

    def __str__(self):
        return f"Invite from {self.inviter} to {self.receiver}, Status: {self.status}"


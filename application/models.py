from django.db import models
from Auth.models import User

APPLICATION_STATUS = [
    ('submitted', 'Submitted'),
    ('under_review', 'Under Review'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]
# Create your models here.
class Application(models.Model):
    proposal = models.TextField()
    status = models.CharField(choices=APPLICATION_STATUS, max_length=20,default='submitted')
    approve = models.BooleanField(default=False)
    team = models.ForeignKey('post.Team', related_name='applications', on_delete=models.CASCADE,null=1)
    student = models.ForeignKey(User, related_name='applications', on_delete=models.CASCADE,null=1)
    acceptedby = models.ManyToManyField("Auth.User", verbose_name=("accepteduser"))
    atachedfile=models.URLField(max_length=200, null=True, blank=True)
    links = models.JSONField(null=True, blank=True)
    def __str__(self):
        return f"Application by {self.student} - Status: {self.status}"

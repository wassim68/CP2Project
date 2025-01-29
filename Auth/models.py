from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.dispatch import receiver
from django.db.models.signals import post_save
types=[
    ('Student','Student'),
    ('Company','Company'),
    ('Admin','Admin')
]
CATEGORY_CHOICES = [
        ('EC', 'Economics'),
        ('CS', 'Computer Science & IT'),
        ('EN', 'Engineering'),
        ('HL', 'Healthcare'),
        ('BM', 'Business & Management'),
        ('LW', 'Law'),
        ('ED', 'Education'),
        ('AH', 'Arts & Humanities'),
    ]
Gendre=[
    ('M','Men'),
    ('F','Female'),
    ('P','Prefer not to say')
]
class company(models.Model):
    category=models.CharField( max_length=50,choices=CATEGORY_CHOICES)
    opportunity=models.ForeignKey('post.Opportunity', verbose_name=("oppertune"), on_delete=models.CASCADE,null=True)
    REQUIRED_FIELDS = ['category']

class Skills(models.Model):
    name=models.TextField()

class Student(models.Model):
    education=models.CharField(max_length=50)
    gendre=models.CharField(choices=Gendre, max_length=50,default='P')
    category=models.CharField( max_length=50,choices=CATEGORY_CHOICES)
    Skills=models.ManyToManyField("Auth.skills", verbose_name=("Skills"))
    rating=models.IntegerField(default=5)
    REQUIRED_FIELDS = ['education']


class MyAccountManager(BaseUserManager):
    def create_user(self,email,name,type,password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not name:
            raise ValueError("Users must have a username")
        if not type:
            raise ValueError("User must defined the type")
        user = self.model(
            email = self.normalize_email(email),
            name = name,
            type=type
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self,email,name,password):
        user = self.create_user(
            email = self.normalize_email(email),
            password = password,
            name = name,
            type='Admin'
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser,PermissionsMixin):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    Number=models.IntegerField(null=True)
    company=models.OneToOneField("Auth.company", verbose_name=("company"),null=True,on_delete=models.CASCADE)
    Student=models.OneToOneField("Auth.Student", verbose_name=("Students"), null=True,on_delete=models.CASCADE)
    profilepic=models.ImageField(upload_to='images', height_field=None, width_field=None, max_length=None,null=True)
    type=models.CharField( choices=types,max_length=50)
    date_joined = models.DateField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)


    objects = MyAccountManager()
    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = ['email']
    def __str__(self):      
        return self.name
    def has_perm(self, perm, obj=None):
     return self.is_superuser or super().has_perm(perm, obj)


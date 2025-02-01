from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
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
    REQUIRED_FIELDS = ['category']

class Skills(models.Model):
    name=models.TextField(unique=1)
    def __str__(self):
        return self.name
    

class Student(models.Model):
    education=models.CharField(max_length=50)
    gendre=models.CharField(choices=Gendre, max_length=50,default='P')
    category=models.CharField( max_length=50,choices=CATEGORY_CHOICES)
    skills=models.ManyToManyField("Auth.skills", verbose_name=("Skills"))
    rating=models.IntegerField(default=5)
    savedposts=models.ManyToManyField('post.Opportunity', verbose_name=("opportunity"))
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
    place=models.CharField(max_length=50,null=True)
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    number=models.IntegerField(null=True)
    company=models.OneToOneField("company", verbose_name=("company"),null=True,on_delete=models.SET_NULL,related_name="user")
    student=models.OneToOneField("Student", verbose_name=("Students"), null=True,on_delete=models.SET_NULL,related_name="user")
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
    
class Notfications(models.Model):
    user=models.ForeignKey("Auth.User", verbose_name=("user"), on_delete=models.CASCADE)
    description=models.TextField()
    time=models.TimeField(auto_now_add=True)


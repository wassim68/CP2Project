from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import models
from . import serlaizers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from . import permissions
from . import tasks
from numpy import random
from django.core.cache import cache
from post import models as md
from post import serializer as sr
from django.contrib.auth.models import Permission
from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime

class google_auth(APIView):
  def post(self,request):
    pass
class linkedin_auth(APIView):
  def post(self,request):
    pass
class Signup(APIView):
  def post(self,request):
    data=request.data
    type=data.get('type')
    if type:
      if type.lower()=='student':
       ser=serlaizers.UserStudentSerializer(data=data)
       if ser.is_valid():
         ser.save(type='Student')
         user=models.User.objects.get(id=ser.data['id'])
         refresh=RefreshToken.for_user(user)
         access_token = refresh.access_token
         return Response({'user':ser.data,'refresh':str(refresh),'access':str(access_token)})
       return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)
      if type.lower()=='company':
       ser=serlaizers.UserCompanySerializer(data=data)
       if ser.is_valid():
        ser.save(type='Company')
        user=models.User.objects.get(id=ser.data['id'])
        refresh=RefreshToken.for_user(user)
        access_token = refresh.access_token
        return Response({'user':ser.data,'refresh':str(refresh),'access':str(access_token)})
      return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)
    return Response({'add type'},status=status.HTTP_405_METHOD_NOT_ALLOWED)


class Login(APIView):
  def post(self,request):
    name=request.data.get('name')
    email=request.data.get('email')
    password=request.data.get('password')
    try:
      if name:
       user=models.User.objects.get(name=name)
      elif email:
       user=models.User.objects.get(email=email)
      if name or email:
       if user.check_password(password):
        if user.has_perm('Auth.company'):
          ser=serlaizers.UserCompanySerializer(user)
        else:
         ser=serlaizers.UserStudentSerializer(user)
        refresh=RefreshToken.for_user(user)
        access_token = refresh.access_token
        return Response({'user':ser.data,'refresh':str(refresh),'access':str(access_token)})
       return Response({'Password inccorect'},status=status.HTTP_401_UNAUTHORIZED)
      return  Response({'Email or password are requeird'},status=status.HTTP_400_BAD_REQUEST)
    except models.User.DoesNotExist:
      return Response({'User Dosent exist'},status=status.HTTP_404_NOT_FOUND)


class acc(APIView):
  permission_classes=[IsAuthenticated]
  def delete(self,request):
    user=models.User.objects.get(id=request.user.id)
    password=request.data.get('password')
    if password:
      if user.check_password(password):
        user.delete()
        return Response({'user deleted succefuly'})
      return Response({'incorect password'},status=status.HTTP_401_UNAUTHORIZED)
    return Response({'add password'},status=status.HTTP_400_BAD_REQUEST)
  def put(self,request):
    user=request.user
    data=request.data
    if user.company :
      ser=serlaizers.UserCompanySerializer(user,data=data,partial=True)
      if ser.is_valid():
       ser.save()
       return Response(ser.data)
      return Response(ser.errors)
    elif user.student:
      ser=serlaizers.UserStudentSerializer(user,data=data,partial=True)
      if ser.is_valid():
       ser.save()
       return Response(ser.data)
      return Response(ser.errors)
  def get(self,request):
     user=request.user
     if user.company:
       ser=serlaizers.UserCompanySerializer(user)
     elif user.student:
       ser=serlaizers.UserStudentSerializer(user)
     return Response(ser.data)



class ForgotPass(APIView):
  def post(self,request):
    email=request.data.get('email')
    name=request.data.get('name')
    try:
      if email:
       user=models.User.objects.get(email=email)
      elif name:
       user=models.User.objects.get(name=name)
      useremail=user.email
      otp = f"{random.randint(0, 999999):06d}"
      tasks.sendemail.delay(
      message=(
        "You requested to reset your password. Please use the OTP below:<br><br>"
        "<h2 style='color: #007bff; text-align: center;'>{}</h2><br>"
        "This OTP is valid for only 5 minutes.<br><br>"
        "If you didn't request this, please ignore this email.<br><br>"
    ).format(otp),
    subject="Reset Your Password",
    receipnt=[useremail],
    title="Reset Password",
    user=user.name)
      return Response({'otp':otp,'iat':datetime.now()})
    except models.User.DoesNotExist:
      return Response({'user dosnet exist'},status=status.HTTP_404_NOT_FOUND)

class Fcm(APIView):
  permission_classes=[IsAuthenticated]
  def post(self,request):
    user=request.user
    ser=serlaizers.Fcmserlaizer(data=request.data)
    if ser.is_valid():
      ser.save()
      return Response({'suceffuly'})
    return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)



class reset_password(APIView):
  def put(self,request):
    email=request.data.get('email')
    name=request.data.get('name')
    newpassword=request.data.get('password')
    try:
      if newpassword:
         if email:
           user=models.User.objects.get(email=email)
         elif name:
          user=models.User.objects.get(name=name)
         if name or email:
          if user.check_password(newpassword):
            return Response({'pervieuos password'})
          user.set_password(newpassword)
          user.save()
          tasks.sendemail.delay(
           message=(
           "Your password has been successfully reset.<br><br>"
           "If you made this change, you can ignore this email.<br><br>"
            "If you did not request this change, please contact our support immediately.<br><br>"
            ).format(user.name),
            subject="Your Password Has Been Reset",
            receipnt=[user.email],
            title="Password Reset Successful",
            user=user.name)
          return Response({'password changed succefuly'})
         return Response({'Email or name is requeird'},status=status.HTTP_406_NOT_ACCEPTABLE)
      return Response({'password and otp are requeird'},status=status.HTTP_406_NOT_ACCEPTABLE)
    except models.User.DoesNotExist:
      return Response({'user dosent exist'},status=status.HTTP_404_NOT_FOUND)
    
class getuser(APIView):
  permission_classes=[IsAuthenticated]
  def get(self,request,id):
    try:
      user=models.User.objects.get(id=id)
      if user.company:
       ser=serlaizers.UserCompanySerializer(user)
      elif user.student:
        ser=serlaizers.UserStudentSerializer(user)
      return Response(ser.data)
    except Exception :
      return Response({'user dosent exist'},status=status.HTTP_404_NOT_FOUND)


  

class savedpost(APIView):
  permission_classes=[IsAuthenticated,permissions.IsStudent]
  def post(self,request,id):
    user =request.user 
    try:
       post=md.Opportunity.objects.get(id=id)
       student=user.student
       student.savedposts.add(post)
       student.save()
       return Response({'saved succefluy'})
    except Exception :
      return Response({"post does'nt exist"},status=status.HTTP_404_NOT_FOUND)
  def delete(self,request,id):
    user=request.user
    try:
        post=md.Opportunity.objects.get(id=id)
        if not user.student.savedposts.filter(id=post.id).exists():
          return Response({"item is'nt saved"})
        user.student.savedposts.remove(post)
        user.student.save()
        return Response({'post removed succefuly'})
    except Exception as e:
      return Response({'eror':str(e)},status=status.HTTP_404_NOT_FOUND)

class post(APIView):
  permission_classes=[IsAuthenticated,permissions.IsStudent]
  def get(self,request):
    user=request.user
    ser=sr.opportunity_serializer(user.student.savedposts,many=True)
    return Response(ser.data)








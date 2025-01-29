from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import models
from . import serlaizers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
# Create your views here.
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
         return Response({'user':ser.data,'refresh_token':str(refresh),'access_token':str(access_token)})
       return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)
      if type.lower()=='company':
       ser=serlaizers.UserCompanySerializer(data=data)
       if ser.is_valid():
        ser.save(type='Company')
        user=models.User.objects.get(id=ser.data['id'])
        refresh=RefreshToken.for_user(user)
        access_token = refresh.access_token
        return Response({'user':ser.data,'refresh_token':str(refresh),'access_token':str(access_token)})
      return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)  
    return Response({'add type'},status=status.HTTP_400_BAD_REQUEST)
    
class Login(APIView):
  def post(self,request):
    name=request.data.get('name')
    password=request.data.get('password')
    try:
      user=models.User.objects.get(name=name)
      if user.check_password(password):
        if user.company:
          ser=serlaizers.UserCompanySerializer(user)
        else:
          ser=serlaizers.UserStudentSerializer(user)
        refresh=RefreshToken.for_user(user)
        access_token = refresh.access_token
        return Response({'user':ser.data,'refresh_token':str(refresh),'access_token':str(access_token)})
      return Response({'Password inccorect'},status=status.HTTP_401_UNAUTHORIZED)
    except models.User.DoesNotExist:
      return Response({'User Dosent exist'},status=status.HTTP_404_NOT_FOUND)

class Deleteacc(APIView):
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

class ForgotPass(APIView):
  def post(self,request):
    pass

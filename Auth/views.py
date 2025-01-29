from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import models
from . import serlaizers
# Create your views here.
class Login(APIView):
  def post(self,request):
    data=request.data
    type=data.get('type')
    if type.lower()=='student':
      ser=serlaizers.UserStudentSerializer(data=data)
    if type.lower()=='company':
      ser=serlaizers.UserCompanySerializer(data=data)
      if ser.is_valid():
        ser.save(type='Company')
        return Response(ser.data)
      return Response(ser.errors)  
    
class Signup(APIView):
  def post(self,request):
    pass

class Deleteacc(APIView):
  def delete(self,request):
    pass

class ForgotPass(APIView):
  def post(self,request):
    pass

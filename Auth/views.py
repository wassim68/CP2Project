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
    ser=serlaizers.UserCompanySerializer(data=data)
    if ser.is_valid():
      ser.save()
      return Response(ser.data)
    return Response(ser.errors,status=status.HTTP_406_NOT_ACCEPTABLE)
    
   
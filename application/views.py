from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from . import serlaizers as serializer
from post import serializer as sr
from . import models
from .models import Application
from post.models import Opportunity,Team
from Auth import permissions
from rest_framework.permissions import IsAuthenticated
from Auth import tasks as tsk
# Create your views here.
class applications(APIView):
    permission_classes=[IsAuthenticated,permissions.IsStudent]
    def post(self,request,id):
        user=request.user 
        data=request.data
        team=data.pop('team',None)
        try:
         post=Opportunity.objects.get(id=id)
         if post.status =='open':
             if team:
                 team=Team.objects.get(name='cite 6')
                 if post.applications.filter(team__name=team.name).exists():
                     return Response({"You are already entre this "}, status=status.HTTP_400_BAD_REQUEST)
                 student_emails = list(team.students.values_list('email', flat=True))
                 ser=serializer.application_serializer(data=data)
                 if ser.is_valid():
                      ser.save(team=team)
                      post.applications.add(ser.data['id'])
                      tsk.sendemail.delay(
    message=(
        "You have been invited to participate in <strong>'{request_title}'</strong>, "
        "a {request_type} that requires team approval.<br><br>"
        "<strong>📌 Details:</strong><br>"
        "- <strong>Title:</strong> {request_title}<br>"
        "- <strong>Description:</strong> {request_description}<br>"
        "- <strong>Requested By:</strong> {request_creator}<br>"
        "- <strong>Approval Needed By:</strong> {deadline_date}<br><br>"
        "To accept the request, please click the link below:<br><br>"
        "<a href='http://172.20.48.1:8000/app/{request_id}/accept/' "
        "style='background-color:#007bff; color:white; padding:10px 15px; text-decoration:none; "
        "border-radius:5px;'>Accept Request</a><br><br>"
        "If you do not take action, the request will remain pending until all team members respond.<br><br>"
        "If you have any questions, feel free to reach out.<br><br>"
        "Best regards,<br>"
        "<strong>The [Platform Name] Team</strong><br><br>"
        "Need assistance? Contact us at <a href='mailto:support@email.com'>support@email.com</a>."
    ).format( 
        request_title=post.title,
        request_type=post.Type,  
        request_description=post.description,
        request_creator=team.name,
        deadline_date=post.endday,
        request_id=ser.data['id']  
    ),
    subject="Action Required: Approve Request for Internship/Challenge",
    receipnt=student_emails,
    title="Request Approval Needed",
    user='moo'
)
                 return Response(ser.data)
             else :
                if post.applications.filter(student=user).exists():
                    return Response({"You have already applied for this opportunity"}, status=status.HTTP_400_BAD_REQUEST) 
                ser=serializer.application_serializer(data=data)
                if ser.is_valid():
                    ser.save(student=user,approve=True)
                    post.applications.add(ser.data['id'])
                    return Response(ser.data)
                return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)
         return Response({'the opportunity is closed'},status=status.HTTP_226_IM_USED)
        except Team.DoesNotExist:
            return Response({"team does'nt exist"},status=status.HTTP_404_NOT_FOUND)
        except Opportunity.DoesNotExist:
            return Response({"post does'nt exist"},status=status.HTTP_404_NOT_FOUND)
        
class accept_application(APIView):
    permission_classes=[IsAuthenticated,permissions.IsStudent]
    def post(self,request,id):
        user=request.user
        try:
            app=Application.objects.get(id=id)
            app.acceptedby.add(user)
            if app.acceptedby.count()==app.team.students.count():
                app.approve=True
            app.save()
            return Response({'accepted'})
        except Application.DoesNotExist:
            return Response({"this application does'nt exist"},status=status.HTTP_404_NOT_FOUND)

class reject_application(APIView):
    permission_classes=[IsAuthenticated,permissions.IsStudent]
    def post(self,request,id):
        user=request.user
        try:
            app=Application.objects.get(id=id)
            if app.acceptedby.filter(name=user.name).exists():
              app.acceptedby.remove(user)
            app.save()
            return Response({'rejected'})
        except Application.DoesNotExist:
            return Response({"this application does'nt exist"},status=status.HTTP_404_NOT_FOUND)

class deleteapplication(APIView):
    permission_classes=[IsAuthenticated,permissions.IsStudent]
    def delete(self,request,id):
        user=request.user
        try:
            app=Application.objects.get(student=user,opportunities__id=id)
            app.delete()
            return Response({'item deleted'})
        except Application.DoesNotExist:
            return Response({"this application does'nt exist"},status=status.HTTP_404_NOT_FOUND)
class application_crud(APIView):
    permission_classes=[IsAuthenticated,permissions.IsStudent]
    def get(self,request):
        user=request.user
        try:
            app=Application.objects.filter(Q(student=user),Q(approve=True))
            post=Opportunity.objects.filter(applications__in=app)
            ser=sr.opportunity_serializer(post,many=True)
            se=serializer.application_serializer(app,many=True)
            return Response({'post':ser.data,'application':se.data})
        except Exception as e:
            return Response({'eror':str(e)},status=status.HTTP_404_NOT_FOUND)
class company_app_management(APIView):
    permission_classes=[IsAuthenticated,permissions.IsCompany]
    def get(self,request,id):
        user=request.user
        try:
            post=Opportunity.objects.filter(company=user,id=id)
            app=models.Application.objects.filter(opportunities__in=post,approve=True)
            ser=serializer.application_serializer(app,many=True)
            return Response(ser.data)
        except Exception as e:
            return Response(e,status=status.HTTP_404_NOT_FOUND)
class choose_app(APIView):
    permission_classes=[IsAuthenticated,permissions.IsCompany]
    def post(self,request,id):
        user=request.user 
        pass






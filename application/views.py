from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from . import serlaizers as serializer
from post import serializer as sr
from . import models
from .models import Application
from post.models import Opportunity,Team
from Auth.serlaizers import UserCompanySerializer
from Auth import permissions
from rest_framework.permissions import IsAuthenticated
from Auth import tasks as tsk
from drf_yasg.utils import swagger_auto_schema
from . import documents
from elasticsearch_dsl.query import Q as Query
from drf_yasg import openapi

# Create your views here.
class applications(APIView):
    permission_classes=[IsAuthenticated,permissions.IsStudent]
    @swagger_auto_schema(
        operation_description="Submit an application for an opportunity. This endpoint allows students to apply for opportunities either individually or as part of a team.",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="Opportunity ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING),
            openapi.Parameter('team', openapi.IN_HEADER, description="Team name", type=openapi.TYPE_STRING, required=False)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Application message'),
            }
        ),
        responses={
            200: openapi.Response(description="Application created successfully"),
            400: 'Invalid data provided or already applied',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Opportunity or team not found',
            226: 'Opportunity is closed'
        }
    )
    def post(self,request,id):
        user=request.user 
        data=request.data
        team=request.headers.get('team')
        try:
         post=Opportunity.objects.get(id=id)
         if post.status =='open':
             if team:
                 team=Team.objects.get(name=team)
                 if post.applications.filter(team__name=team.name).exists():
                     return Response({"You are already entre this "}, status=status.HTTP_400_BAD_REQUEST)
                 student_emails = [
                      email for email in team.students.values_list('email', flat=True)
                      if email != request.user.email
                       ]
                 ser=serializer.application_serializer(data=data)
                 if ser.is_valid():
                      ser.save(team=team)
                      ser.instance.acceptedby.add(user)
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
                    ser.save(student=user,approve=True,status='under_review')
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
    @swagger_auto_schema(
        operation_description="Accept a team application. This endpoint allows team members to approve an application submitted on behalf of their team.",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="Application ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(description="Application accepted successfully"),
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Application not found'
        }
    )
    def post(self,request,id):
        user=request.user
        try:
            app=Application.objects.get(id=id)
            op=app.opportunities.all().first()
            app.acceptedby.add(user)
            if app.acceptedby.count()==app.team.students.count():
                app.approve=True
                app.status='under_review'
            app.save()
            return Response({'accepted'})
        except Application.DoesNotExist:
            return Response({"this application does'nt exist"},status=status.HTTP_404_NOT_FOUND)

class reject_application(APIView):
    permission_classes=[IsAuthenticated,permissions.IsStudent]
    @swagger_auto_schema(
        operation_description="Reject a team application. This endpoint allows team members to reject an application submitted on behalf of their team.",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="Application ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(description="Application rejected successfully"),
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Application not found'
        }
    )
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
    @swagger_auto_schema(
        operation_description="Delete an application. This endpoint allows students to withdraw their applications for opportunities.",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="Application ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(description="Application deleted successfully"),
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Application not found'
        }
    )
    def delete(self,request,id):
        user=request.user
        try:
            app=Application.objects.get(id=id,student=user)
            app.delete()
            return Response({'item deleted'})
        except Application.DoesNotExist:
            return Response({"this application does'nt exist"},status=status.HTTP_404_NOT_FOUND)

class application_crud(APIView):
    permission_classes=[IsAuthenticated,permissions.IsStudent]
    @swagger_auto_schema(
        operation_description="Get all applications for the authenticated student. This endpoint returns a list of opportunities the student has applied for and their application details.",
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(
                description="Applications retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'post': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'application': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT))
                    }
                )
            ),
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not found'
        }
    )
    def get(self,request):
        user=request.user
        try:
            app=Application.objects.filter(Q(student=user)|Q(team__students=user))
            post=Opportunity.objects.filter(applications__in=app)
            ser=sr.opportunity_serializer(post,many=True)
            se=serializer.application_serializer(app,many=True)
            return Response({'post':ser.data,'application':se.data})
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_404_NOT_FOUND)

class company_app_management(APIView):
    permission_classes=[IsAuthenticated,permissions.IsCompany]
    @swagger_auto_schema(
        operation_description="Get all approved applications for a specific opportunity. This endpoint allows companies to view applications that have been approved by teams.",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="Opportunity ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(
                description="Applications retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT)
                )
            ),
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not found'
        }
    )
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
    @swagger_auto_schema(
        operation_description="Select applications to accept for an opportunity. This endpoint allows companies to choose which applications to accept and close the opportunity.",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="Opportunity ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER), description='List of application IDs to accept')
            },
            required=['id']
        ),
        responses={
            200: openapi.Response(
                description="Applications accepted successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT)
                )
            ),
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Opportunity not found'
        }
    )
    def post(self,request,id):
        ids=request.data.get('id',[])
        user=request.user
        try:
         post=Opportunity.objects.get(id=id,company=user)
         all=post.applications.all()
         all.update(status='rejected')
         app=post.applications.filter(id__in=ids)
         app.update(status='accepted')
         post.status='closed'
         post.save()
         ser=serializer.application_serializer(app,many=True)
         return Response(ser.data)
        except Opportunity.DoesNotExist:
            return Response({'post does not exist'},status=status.HTTP_404_NOT_FOUND)

class search(APIView):
    permission_classes=[IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Search for opportunities and companies. This endpoint allows users to search for opportunities and companies based on a query string.",
        manual_parameters=[
            openapi.Parameter('q', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(
                description="Search results retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'opportunity': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'company': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT))
                    }
                )
            ),
            400: 'Query is required',
            401: 'Unauthorized',
            404: 'Not found'
        }
    )
    def get(self,request):
        user=request.user
        try:
            query = request.GET.get('q', '').strip()
            if not query:
                return Response({'error':'query is required'},status=status.HTTP_400_BAD_REQUEST)
            post_query = Query("prefix", title=query.lower())
            post=documents.Opportunitydocument.search().query(post_query)
            company_query = Query("prefix", name=query.lower())
            company = documents.companyDocument.search().query(company_query)
            if post:
             post=post.to_queryset()
            ser1=sr.opportunity_serializer(post,many=True)
            if company:
             company=company.to_queryset()
             company=company.filter(type='Company')
            ser2=UserCompanySerializer(company,many=True)
            return Response({'opportunity':ser1.data,'company':ser2.data})
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_404_NOT_FOUND)


class search_applied(APIView):
    authentication_classes = [IsAuthenticated,permissions.IsStudent]

    




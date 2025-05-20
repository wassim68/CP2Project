from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from . import serlaizers as serializer
from post import serializer as sr
from . import models
from .models import Application
from post.models import Opportunity,Team
from Auth.serlaizers import UserCompanySerializer,UserStudentSerializer
from Auth import permissions
from rest_framework.permissions import IsAuthenticated
from Auth import tasks as tsk

from drf_yasg.utils import swagger_auto_schema
from . import documents
from elasticsearch_dsl.query import Q as Query
from drf_yasg import openapi
from post.pagination import CustomPagination
from django.shortcuts import render

# Create your views here.
class applications(APIView):
    permission_classes=[IsAuthenticated,permissions.IsStudent]
    @swagger_auto_schema(
        operation_description="Submit an application for an opportunity. This endpoint allows students to apply for opportunities either individually or as part of a team.",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="Opportunity ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING),
            openapi.Parameter('team', openapi.IN_HEADER, description="Team name (optional)", type=openapi.TYPE_STRING, required=False)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['message'],
            properties={
                'message': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='Application message explaining why you are interested in this opportunity',
                    example="I am interested in this opportunity because..."
                ),
            },
            example={
                "message": "I am interested in this opportunity because of my experience in..."
            }
        ),
        responses={
            200: openapi.Response(
                description="Application created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'approve': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden"),
            404: openapi.Response(description="Opportunity or team not found"),
            226: openapi.Response(description="Opportunity is closed")
        },
        tags=['Applications']
    )
    def post(self,request,id):
        user=request.user 
        data=request.data
        team = request.query_params.get('team')
        try:
         post=Opportunity.objects.get(id=id)
         if post.status =='open':
             if team:
                 team=Team.objects.get(id=team)
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
        deadline_date=post.enddate,
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
            200: openapi.Response(
                description="Application accepted successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden"),
            404: openapi.Response(description="Application not found")
        },
        tags=['Applications']
    )
    def post(self,request,id):
        user=request.user
        try:
            app=Application.objects.get(id=id)
            if not app:
                return render(request, 'application_choice.html', {
                    'error': 'Application not found'
                })
            op=app.opportunities.all().first()
            app.acceptedby.add(user)
            if app.acceptedby.count()==app.team.students.count():
                app.approve=True
                app.status='under_review'
            app.save()
            return render(request, 'application_accepted.html')
        except Application.DoesNotExist:
            return render(request, 'application_choice.html', {
                'error': 'Application not found'
            })

class reject_application(APIView):
    permission_classes=[IsAuthenticated,permissions.IsStudent]
    @swagger_auto_schema(
        operation_description="Reject a team application. This endpoint allows team members to reject an application submitted on behalf of their team.",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="Application ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(
                description="Application rejected successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden"),
            404: openapi.Response(description="Application not found")
        },
        tags=['Applications']
    )
    def post(self,request,id):
        user=request.user
        try:
            app=Application.objects.get(id=id)
            if not app:
                return render(request, 'application_choice.html', {
                    'error': 'Application not found'
                })
            if app.acceptedby.filter(name=user.name).exists():
                app.acceptedby.remove(user)
            app.save()
            return render(request, 'application_rejected.html')
        except Application.DoesNotExist:
            return render(request, 'application_choice.html', {
                'error': 'Application not found'
            })

class deleteapplication(APIView):
    permission_classes=[IsAuthenticated,permissions.IsStudent]
    @swagger_auto_schema(
        operation_description="Delete an application. This endpoint allows students to withdraw their applications for opportunities.",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="Application ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(
                description="Application deleted successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden"),
            404: openapi.Response(description="Application not found")
        },
        tags=['Applications']
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
                        'application': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                                    'approve': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                                    'post': openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                            'title': openapi.Schema(type=openapi.TYPE_STRING),
                                            'description': openapi.Schema(type=openapi.TYPE_STRING),
                                            'Type': openapi.Schema(type=openapi.TYPE_STRING),
                                            'category': openapi.Schema(type=openapi.TYPE_STRING),
                                            'skill_input': openapi.Schema(type=openapi.TYPE_STRING),
                                            'worktype': openapi.Schema(type=openapi.TYPE_STRING)
                                        }
                                    )
                                }
                            )
                        )
                    }
                )
            ),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden"),
            404: openapi.Response(description="Not found")
        },
        tags=['Applications']
    )
    def get(self,request):
        user=request.user
        team=request.query_params.get('team')
        try:
            if team:
                app=Application.objects.filter(team__id=team)
            else:
                app=Application.objects.filter(Q(student=user)|Q(team__students=user))
            s=[]
            for each in app :
             se=serializer.application_serializer(each)
             post=Opportunity.objects.get(applications=each)
             ser=sr.opportunity_serializer(post)
             se_data = se.data.copy()  
             se_data.update({'post':ser.data})
             s.append(se_data)
            return Response({'application':s})
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
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'message': openapi.Schema(type=openapi.TYPE_STRING),
                            'status': openapi.Schema(type=openapi.TYPE_STRING),
                            'approve': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                            'student': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'email': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            )
                        }
                    )
                )
            ),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden"),
            404: openapi.Response(description="Not found")
        },
        tags=['Applications']
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
            required=['id'],
            properties={
                'id': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description='List of application IDs to accept'
                )
            },
            example={
                "id": [1, 2, 3]
            }
        ),
        responses={
            200: openapi.Response(
                description="Applications accepted successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden"),
            404: openapi.Response(description="Opportunity not found")
        },
        tags=['Applications']
    )
    def post(self,request,id):
        ids=request.data.get('id',[])
        user=request.user
        try:
         post=Opportunity.objects.get(id=id,company=user)
         all=post.applications.all()
         app=post.applications.filter(id__in=ids)
         app.update(status='accepted')
         for each in app:
             if each.team:
                 for each1 in each.team.students.all():
                     each1.student.experience+=[{'title':post.title,'company':user.name,'start':post.startdate,'end':post.enddate}]
                     each1.student.save()
             else :
                 each.student.student.experience+=[{'title':post.title,'company':user.name,'start':post.startdate,'end':post.enddate}]
                 each.student.student.save()
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
                        'opportunity': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'title': openapi.Schema(type=openapi.TYPE_STRING),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING),
                                    'Type': openapi.Schema(type=openapi.TYPE_STRING),
                                    'category': openapi.Schema(type=openapi.TYPE_STRING),
                                    'skill_input': openapi.Schema(type=openapi.TYPE_STRING),
                                    'worktype': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            )
                        ),
                        'company': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'email': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            )
                        )
                    }
                )
            ),
            400: openapi.Response(description="Query is required"),
            401: openapi.Response(description="Unauthorized"),
            404: openapi.Response(description="Not found")
        },
        tags=['Search']
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
    permission_classes = [IsAuthenticated,permissions.IsStudent]
    @swagger_auto_schema(
        operation_description="Search for applications. This endpoint allows students to search for their applications based on a query string.",
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_QUERY, description="Title of the application to search for", type=openapi.TYPE_STRING),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        responses={
            200: openapi.Response(
                description="Search results retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                                    'approve': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                                    'post': openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                            'title': openapi.Schema(type=openapi.TYPE_STRING),
                                            'description': openapi.Schema(type=openapi.TYPE_STRING),
                                            'Type': openapi.Schema(type=openapi.TYPE_STRING),
                                            'category': openapi.Schema(type=openapi.TYPE_STRING),
                                            'skill_input': openapi.Schema(type=openapi.TYPE_STRING),
                                            'worktype': openapi.Schema(type=openapi.TYPE_STRING)
                                        }
                                    )
                                }
                            )
                        )
                    }
                )
            ),
            400: openapi.Response(description="Title is required"),
            401: openapi.Response(description="Unauthorized"),
            404: openapi.Response(description="Not found")
        },
        tags=['Search']
    )
    def get(self,request):
        title = request.query_params.get('title')
    
        if title is None:
            return Response({"details": "title not provided"}, status=status.HTTP_400_BAD_REQUEST)

        student = request.user.student

        if student is None:
             return Response({"details": "must be a student"}, status=status.HTTP_401_UNAUTHORIZED)


        q = Query("multi_match", query=title, fields=["title"], fuzziness="auto")

        search_qs = documents.ApplicationDocument.search().query(q).execute()

        ids = [hit.meta.id for hit in search_qs.hits]

        md_qs = request.user.applications.filter(id__in = ids)

        paginator = CustomPagination()

        paginated_qs = paginator.paginate_queryset(md_qs,request)

        ser = serializer.application_serializer(paginated_qs,many = True)

        return paginator.get_paginated_response(ser.data)

class webapp(APIView):
    permission_classes=[IsAuthenticated,permissions.IsCompany]
    def get(self,request,id):
        user=request.user
        try:
            app=models.Application.objects.filter(id=id,approve=True).first()
            if app.team:
                user=app.team
                ser=serializer.application_serializer(app)
                ser1=sr.team_serializer(user)
                return Response({'application':ser.data,'team':ser1.data,'type':'team'})
            else:
                user=app.student
                ser=serializer.application_serializer(app)
                ser1=UserStudentSerializer(user)
                return Response({'application':ser.data,'user':ser1.data,'type':'user'})
        except Exception as e:
            return Response(e,status=status.HTTP_404_NOT_FOUND)




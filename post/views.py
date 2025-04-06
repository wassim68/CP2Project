from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from post.models import Opportunity,Team
from post import serializer
from . import models
from Auth.models import User,company,Student
from Auth.serlaizers import UserStudentSerializer
from itertools import chain
from Auth import permissions
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    operation_description="Get all opportunities. For companies, this returns only their own opportunities. For other users, this returns all opportunities.",
    manual_parameters=[
        openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'description': openapi.Schema(type=openapi.TYPE_STRING),
            'Type': openapi.Schema(type=openapi.TYPE_STRING),
            'category': openapi.Schema(type=openapi.TYPE_STRING),
            'skill_input': openapi.Schema(type=openapi.TYPE_STRING),
            'worktype': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={
        200: openapi.Response(description="Operation successful"),
        201: openapi.Response(description="Created successfully"),
        204: openapi.Response(description="Deleted successfully"),
        400: 'Invalid data provided',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not found'
    }
)
class opportunity_crud(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        user = request.user
        if user.has_perm('Auth.company'):
            post = models.Opportunity.objects.filter(company=user)
        else:
            post = models.Opportunity.objects.all()
        ser = serializer.opportunity_serializer(post, many=True)
        return Response(ser.data)
    
    @swagger_auto_schema(
        operation_description="Create a new opportunity. This endpoint allows companies to post new opportunities for students to apply.",
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'Type': openapi.Schema(type=openapi.TYPE_STRING),
                'category': openapi.Schema(type=openapi.TYPE_STRING),
                'skill_input': openapi.Schema(type=openapi.TYPE_STRING),
                'worktype': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(description="Operation successful"),
            201: openapi.Response(description="Created successfully"),
            204: openapi.Response(description="Deleted successfully"),
            400: 'Invalid data provided',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not found'
        }
    )
    def post(self, request):
        user = request.user
        if user.has_perm('Auth.company'):
            ser = serializer.opportunity_serializer(data=request.data)
            if ser.is_valid():
                ser.save(company=user)
                return Response(ser.data, status=status.HTTP_201_CREATED)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'you are not a company'}, status=status.HTTP_403_FORBIDDEN)
    
    @swagger_auto_schema(
        operation_description="Update an existing opportunity. This endpoint allows companies to modify details of their posted opportunities.",
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'Type': openapi.Schema(type=openapi.TYPE_STRING),
                'category': openapi.Schema(type=openapi.TYPE_STRING),
                'skill_input': openapi.Schema(type=openapi.TYPE_STRING),
                'worktype': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(description="Operation successful"),
            201: openapi.Response(description="Created successfully"),
            204: openapi.Response(description="Deleted successfully"),
            400: 'Invalid data provided',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not found'
        }
    )
    def put(self, request):
        user = request.user
        if user.has_perm('Auth.company'):
            try:
                post = models.Opportunity.objects.get(id=request.data['id'], company=user)
                ser = serializer.opportunity_serializer(post, data=request.data, partial=True)
                if ser.is_valid():
                    ser.save()
                    return Response(ser.data)
                return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
            except models.Opportunity.DoesNotExist:
                return Response({'post does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'you are not a company'}, status=status.HTTP_403_FORBIDDEN)
    
    @swagger_auto_schema(
        operation_description="Delete an opportunity. This endpoint allows companies to remove their posted opportunities.",
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'Type': openapi.Schema(type=openapi.TYPE_STRING),
                'category': openapi.Schema(type=openapi.TYPE_STRING),
                'skill_input': openapi.Schema(type=openapi.TYPE_STRING),
                'worktype': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(description="Operation successful"),
            201: openapi.Response(description="Created successfully"),
            204: openapi.Response(description="Deleted successfully"),
            400: 'Invalid data provided',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not found'
        }
    )
    def delete(self, request):
        user = request.user
        if user.has_perm('Auth.company'):
            try:
                post = models.Opportunity.objects.get(id=request.data['id'], company=user)
                post.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except models.Opportunity.DoesNotExist:
                return Response({'post does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'you are not a company'}, status=status.HTTP_403_FORBIDDEN)

@swagger_auto_schema(
    operation_description="Get all teams for the authenticated student. This endpoint returns a list of teams that the student is a member of.",
    manual_parameters=[
        openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'name': openapi.Schema(type=openapi.TYPE_STRING),
            'emails': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
        }
    ),
    responses={
        200: openapi.Response(description="Operation successful"),
        201: openapi.Response(description="Created successfully"),
        204: openapi.Response(description="Deleted successfully"),
        400: 'Invalid data provided',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not found'
    }
)
class team_crud(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        user = request.user
        if user.has_perm('Auth.student'):
            team = models.Team.objects.filter(students=user)
            ser = serializer.team_serializer(team, many=True)
            return Response(ser.data)
        return Response({'you are not a student'}, status=status.HTTP_403_FORBIDDEN)
    
    @swagger_auto_schema(
        operation_description="Create a new team. This endpoint allows students to create teams for collaborative applications.",
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'emails': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
            }
        ),
        responses={
            200: openapi.Response(description="Operation successful"),
            201: openapi.Response(description="Created successfully"),
            204: openapi.Response(description="Deleted successfully"),
            400: 'Invalid data provided',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not found'
        }
    )
    def post(self, request):
        user = request.user
        if user.has_perm('Auth.student'):
            ser = serializer.team_serializer(data=request.data)
            if ser.is_valid():
                ser.save()
                team = models.Team.objects.get(id=ser.data['id'])
                team.students.add(user)
                return Response(ser.data, status=status.HTTP_201_CREATED)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'you are not a student'}, status=status.HTTP_403_FORBIDDEN)
    
    @swagger_auto_schema(
        operation_description="Update an existing team. This endpoint allows students to modify details of their teams.",
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'emails': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
            }
        ),
        responses={
            200: openapi.Response(description="Operation successful"),
            201: openapi.Response(description="Created successfully"),
            204: openapi.Response(description="Deleted successfully"),
            400: 'Invalid data provided',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not found'
        }
    )
    def put(self, request):
        user = request.user
        if user.has_perm('Auth.student'):
            try:
                team = models.Team.objects.get(id=request.data['id'], students=user)
                ser = serializer.team_serializer(team, data=request.data, partial=True)
                if ser.is_valid():
                    ser.save()
                    return Response(ser.data)
                return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
            except models.Team.DoesNotExist:
                return Response({'team does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'you are not a student'}, status=status.HTTP_403_FORBIDDEN)
    
    @swagger_auto_schema(
        operation_description="Delete a team. This endpoint allows students to remove their teams.",
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'emails': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
            }
        ),
        responses={
            200: openapi.Response(description="Operation successful"),
            201: openapi.Response(description="Created successfully"),
            204: openapi.Response(description="Deleted successfully"),
            400: 'Invalid data provided',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not found'
        }
    )
    def delete(self, request):
        user = request.user
        if user.has_perm('Auth.student'):
            try:
                team = models.Team.objects.get(id=request.data['id'], students=user)
                team.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except models.Team.DoesNotExist:
                return Response({'team does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'you are not a student'}, status=status.HTTP_403_FORBIDDEN)

@swagger_auto_schema(
    operation_description="Add a student to a team. This endpoint allows team members to add other students to their teams.",
    manual_parameters=[
        openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'teamid': openapi.Schema(type=openapi.TYPE_INTEGER),
            'userid': openapi.Schema(type=openapi.TYPE_INTEGER),
            'useremail': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={
        200: openapi.Response(description="Operation successful"),
        400: 'Invalid data provided',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not found'
    }
)
class team_managing(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Add a student to a team. This endpoint allows team members to add other students to their teams.",
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'teamid': openapi.Schema(type=openapi.TYPE_INTEGER),
                'userid': openapi.Schema(type=openapi.TYPE_INTEGER),
                'useremail': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(description="Operation successful"),
            400: 'Invalid data provided',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not found'
        }
    )
    def put(self, request):
        user = request.user
        if user.has_perm('Auth.student'):
            try:
                team = models.Team.objects.get(id=request.data['teamid'], students=user)
                if 'userid' in request.data:
                    student = models.User.objects.get(id=request.data['userid'])
                    if student.has_perm('Auth.student'):
                        team.students.add(student)
                        return Response({'student added'})
                    return Response({'user is not a student'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'userid is required'}, status=status.HTTP_400_BAD_REQUEST)
            except models.Team.DoesNotExist:
                return Response({'team does not exist'}, status=status.HTTP_404_NOT_FOUND)
            except models.User.DoesNotExist:
                return Response({'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'you are not a student'}, status=status.HTTP_403_FORBIDDEN)
    
    @swagger_auto_schema(
        operation_description="Add a student to a team using their email. This endpoint allows team members to add other students to their teams by email address.",
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'teamid': openapi.Schema(type=openapi.TYPE_INTEGER),
                'userid': openapi.Schema(type=openapi.TYPE_INTEGER),
                'useremail': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(description="Operation successful"),
            400: 'Invalid data provided',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not found'
        }
    )
    def post(self, request):
        user = request.user
        if user.has_perm('Auth.student'):
            try:
                team = models.Team.objects.get(id=request.data['teamid'], students=user)
                if 'useremail' in request.data:
                    student = models.User.objects.get(email=request.data['useremail'])
                    if student.has_perm('Auth.student'):
                        team.students.add(student)
                        return Response({'student added'})
                    return Response({'user is not a student'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'useremail is required'}, status=status.HTTP_400_BAD_REQUEST)
            except models.Team.DoesNotExist:
                return Response({'team does not exist'}, status=status.HTTP_404_NOT_FOUND)
            except models.User.DoesNotExist:
                return Response({'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'you are not a student'}, status=status.HTTP_403_FORBIDDEN)
    
    @swagger_auto_schema(
        operation_description="Remove a student from a team. This endpoint allows team members to remove other students from their teams.",
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="JWT token", type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'teamid': openapi.Schema(type=openapi.TYPE_INTEGER),
                'userid': openapi.Schema(type=openapi.TYPE_INTEGER),
                'useremail': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(description="Operation successful"),
            400: 'Invalid data provided',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not found'
        }
    )
    def delete(self, request):
        user = request.user
        if user.has_perm('Auth.student'):
            try:
                team = models.Team.objects.get(id=request.data['teamid'], students=user)
                if 'userid' in request.data:
                    student = models.User.objects.get(id=request.data['userid'])
                    if student.has_perm('Auth.student'):
                        team.students.remove(student)
                        return Response({'student removed'})
                    return Response({'user is not a student'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'userid is required'}, status=status.HTTP_400_BAD_REQUEST)
            except models.Team.DoesNotExist:
                return Response({'team does not exist'}, status=status.HTTP_404_NOT_FOUND)
            except models.User.DoesNotExist:
                return Response({'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'you are not a student'}, status=status.HTTP_403_FORBIDDEN)


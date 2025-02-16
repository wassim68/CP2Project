
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
from django.views.decorators.cache import cache_page

class opportunity_crud(APIView):
    permission_classes = [IsAuthenticated]
    @cache_page(60*5)
    def get(self,request,*args, **kwargs):
        user = request.user
        if not user.type.lower() == 'company':
            return Response({"details" : "unable to get data"},status=status.HTTP_401_UNAUTHORIZED)

        opportunities = user.opportunity.all()

        if opportunities.exists() :
            #if not user.has_perm('post.view_Opportunity',opportunities):
                #return Response({"detail" : "no permission"},status= status.HTTP_403_FORBIDDEN)
            ser = serializer.opportunity_serializer(instance = opportunities,many = True ) #change to true when fix
            return Response({"data" : ser.data},status=status.HTTP_200_OK)
        return Response({"details" : "no data"},status=status.HTTP_204_NO_CONTENT)
    
    
    
    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        if not user.type.lower() == 'company':
            return Response({"details" : "unable to get data"},status=status.HTTP_401_UNAUTHORIZED)
        ser = serializer.opportunity_serializer(data = data)
        if not ser.is_valid():
            return Response({"details" : "invalid data", "errors": ser.errors},status=status.HTTP_400_BAD_REQUEST)
        #if not user.has_perm('post.post_Opportunity'):
            #return Response({"detail" : "no permission"},status= status.HTTP_403_FORBIDDEN)
        ser.save(company = user)
        return Response({"details" : "created","data" : ser.data},status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        if not user.type.lower() == 'company':
            return Response({"details" : "unable to get data"},status=status.HTTP_401_UNAUTHORIZED)
        id = data.get('id')
        if id is None :
            return Response({"details" : "ID not provided"},status=status.HTTP_400_BAD_REQUEST)
        opp = user.opportunity.filter(id=id).first()
        if opp is None:
            return Response({"details" : "opportunity not found"},status=status.HTTP_404_NOT_FOUND)
        ser = serializer.opportunity_serializer(instance = opp,data = data,partial = True)
        if not ser.is_valid():
            return Response({"details" : "invalid data", "errors": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        #if not user.has_perm('change.view_Opportunity',opp):
            #return Response({"detail" : "no permission"},status= status.HTTP_403_FORBIDDEN)
        ser.save()
        return Response({"details" : "updated"},status=status.HTTP_200_OK)

    def delete(self,request,*args, **kwargs):
        user = request.user
        data = request.data
        if  not user.type.lower() == 'company':
            return Response({"details" : "unable to get data"},status=status.HTTP_401_UNAUTHORIZED)
        id = data.get('id')
        if id is None :
            return Response({"details" : "ID not provided"},status=status.HTTP_400_BAD_REQUEST)
        opp = user.opportunity.filter(id=id).first()
        if opp is not None:
            #if not user.has_perm('delete.view_Opportunity',opportunities):
                #return Response({"detail" : "no permission"},status= status.HTTP_403_FORBIDDEN)
            opp.delete()

        return Response({"details" : "deleted"},status=status.HTTP_200_OK)    


class team_crud(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,*args, **kwargs):
        user = request.user
        if not user.type.lower() == 'student':
            return Response({"details" : "unable to get data"},status=status.HTTP_401_UNAUTHORIZED)

        teams = user.teams.all()

        if teams.exists() :
            ser = serializer.team_serializer(instance = teams,many = True ) 
            return Response({"data" : ser.data},status=status.HTTP_200_OK)
        return Response({"details" : "no data"},status=status.HTTP_204_NO_CONTENT)
    
    
    
    def post(self, request, *args, **kwargs):
        # Ensure the user has the correct permissions (if needed)
        user = request.user
        data = request.data
        
        if not user.type.lower() == 'student':
            return Response({"details": "unable to get data"}, status=status.HTTP_401_UNAUTHORIZED)

        # Extract the list of student emails from the request data
        emails = data.get('emails')
        if not emails:
            return Response({"details": "invalid data", "errors": "students' emails not provided"}, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(email__in=emails, student__isnull=False)

        # If no students are found, return an errorall()

        if not users.exists():
            return Response({"details": "invalid data", "errors": "invalid emails"}, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the team data and create the team instance
        ser = serializer.team_serializer(data=data)
        if not ser.is_valid():
            return Response({"details": "invalid data", "errors": ser.errors}, status=status.HTTP_400_BAD_REQUEST)
        
  
        team_instance = ser.save()

        team_instance.students.set(list(chain(users, [user])))
        team_instance.leader = user
        team_instance.save()

        return Response({"details": "created", "data": ser.data}, status=status.HTTP_201_CREATED)
    
    def put(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        if not user.type.lower() == 'student':
            return Response({"details" : "unable to get data"},status=status.HTTP_401_UNAUTHORIZED)
        id = data.get('id')
        if id is None :
            return Response({"details" : "ID not provided"},status=status.HTTP_400_BAD_REQUEST)
        team = user.owned_teams.all().filter(id=id).first()
        if team is None:
            return Response({"details" : "opportunity not found"},status=status.HTTP_404_NOT_FOUND)
        ser = serializer.team_serializer(instance = team,data = data,partial = True)
        if not ser.is_valid():
            return Response({"details" : "invalid data", "errors": ser.errors},status=status.HTTP_400_BAD_REQUEST)
        #if not user.has_perm('change.view_Opportunity',opp):
            #return Response({"detail" : "no permission"},status= status.HTTP_403_FORBIDDEN)
        ser.save()
        return Response({"details" : "updated"},status=status.HTTP_200_OK)

    def delete(self,request,*args, **kwargs):
        user = request.user
        data = request.data
        if  not user.type.lower() == 'student':
            return Response({"details" : "unable to get data"},status=status.HTTP_401_UNAUTHORIZED)
        id = data.get('id')
        if id is None :
            return Response({"details" : "teamID not provided"},status=status.HTTP_400_BAD_REQUEST)
        
        team = user.owned_teams.all().filter(id=id).first()
        if team is None:
            return Response({"details" : "notfound or no permission"},status=status.HTTP_403_FORBIDDEN)    
        
        team.delete()
        return Response({"details" : "deleted"},status=status.HTTP_200_OK)    

class team_managing(APIView):
    def put(self,request,*args, **kwargs):#kick
        user = request.user
        data = request.data

        if  not user.type.lower() == 'student':
            return Response({"details" : "must be a student"},status=status.HTTP_401_UNAUTHORIZED)
        
        teamid = data.get('teamid')
        if teamid is None :
            return Response({"details" : "teamID not provided"},status=status.HTTP_400_BAD_REQUEST)
        userid = data.get('userid')
        if userid is None :
            return Response({"details" : "userID not provided"},status=status.HTTP_400_BAD_REQUEST)
        
        team = user.owned_teams.filter(id=teamid).first()

        if team is None:
            return Response({"details" : "notfound or no permission"},status=status.HTTP_403_FORBIDDEN) 
        
        removed_user = team.students.filter(id=userid).first()
        if removed_user is None:
            return Response({"details" : "user not found"},status=status.HTTP_404_NOT_FOUND)
        
        if user == removed_user :
            return Response({"details" : "can't kick youself"},status=status.HTTP_403_FORBIDDEN)
        team.students.remove(removed_user)
        return Response({"details" : "kicked"},status=status.HTTP_200_OK)
        
    def post(self,request,*args, **kwargs):#kick
        user = request.user
        data = request.data

        if  not user.type.lower() == 'student':
            return Response({"details" : "must be a student"},status=status.HTTP_401_UNAUTHORIZED)
        
        teamid = data.get('teamid')
        if teamid is None :
            return Response({"details" : "teamID not provided"},status=status.HTTP_400_BAD_REQUEST)
        useremail = data.get('useremail')
        if useremail is None :
            return Response({"details" : "useremail not provided"},status=status.HTTP_400_BAD_REQUEST)
        
        team = user.owned_teams.filter(id=teamid).first()

        if team is None:
            return Response({"details" : "notfound or no permission"},status=status.HTTP_403_FORBIDDEN) 
        
        added_user = User.objects.filter(email=useremail).first()
        if added_user is None:
            return Response({"details" : "user not found"},status=status.HTTP_404_NOT_FOUND)
        
        check_user = team.students.filter(email=useremail).first()
        if check_user == added_user :
            return Response({"details" : "user already in team"},status=status.HTTP_403_FORBIDDEN)
        team.students.add(added_user)
        return Response({"details" : "added"},status=status.HTTP_200_OK)

    def delete(self,request,*args, **kwargs):#kick
        user = request.user
        data = request.data

        if  not user.type.lower() == 'student':
            return Response({"details" : "must be a student"},status=status.HTTP_401_UNAUTHORIZED)
        
        teamid = data.get('teamid')
        if teamid is None :
            return Response({"details" : "teamID not provided"},status=status.HTTP_400_BAD_REQUEST)
        team = user.teams.filter(id=teamid).first()

        if team is None:
            return Response({"details" : "team notfound"},status=status.HTTP_403_FORBIDDEN) 

        team.students.remove(user)

        if not team.students.all().exists() :
            team.delete()
            return Response({"details" : "left , empty team closed "},status=status.HTTP_200_OK) 
        if team.leader == user :
            new_leader = team.students.first()
            team.leader = new_leader
            return Response({"details": f"left, ownership changed to name:{new_leader.name} , id:{new_leader.id}"}, status=status.HTTP_200_OK)
        return Response({"details" : "left"},status=status.HTTP_200_OK) 


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from post import models as md
from application import models as app_models
from . import permissions
from datetime import datetime, timedelta
from django.db.models import Count
from django.db.models.functions import TruncMonth

class CompanyDashboard(APIView):
    permission_classes = [IsAuthenticated, permissions.IsCompany]
    
    def get(self, request, *args, **kwargs):
        # Get the URL path to determine which endpoint to call
        path = request.path_info.strip('/').split('/')
        
        if 'opportunities' in path:
            return self.getCompaniesPostedOpportunities(request)
        elif 'recent' in path:
            return self.getRecentApplications(request)
        elif 'all-applications' in path:
            return self.getAllApplicationsOfCompany(request)
        elif 'applications' in path and 'postId' in kwargs:
            return self.getApplicationByPostId(request, kwargs['postId'])
        elif 'chart-data' in path:
            return self.getApplicationChartData(request)
        elif 'status-counts' in path:
            return self.getStatusCountOfCompany(request)
        elif 'status-pie-chart' in path:
            return self.getApplicationStatusPieChartData(request)
        else:
            return Response({'error': 'Invalid endpoint'}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Get all opportunities posted by the company",
        responses={
            200: openapi.Response(
                description="List of opportunities",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'title': openapi.Schema(type=openapi.TYPE_STRING),
                            'department': openapi.Schema(type=openapi.TYPE_STRING),
                            'location': openapi.Schema(type=openapi.TYPE_STRING),
                            'type': openapi.Schema(type=openapi.TYPE_STRING),
                            'postedDate': openapi.Schema(type=openapi.TYPE_STRING),
                            'applications': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'status': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                )
            )
        }
    )
    def getCompaniesPostedOpportunities(self, request):
        opportunities = md.Opportunity.objects.filter(company=request.user).order_by('-created_at')
        data = []
        for opp in opportunities:
            data.append({
                'id': opp.id,
                'title': opp.title,
                'department': opp.category,
                'location': opp.worktype,
                'type': opp.Type,
                'postedDate': opp.created_at.isoformat(),
                'applications': opp.applications.count(),
                'status': opp.status
            })
        return Response(data)

    @swagger_auto_schema(
        operation_description="Get 5 most recent applications to company opportunities",
        responses={
            200: openapi.Response(
                description="List of recent applications",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'applicantName': openapi.Schema(type=openapi.TYPE_STRING),
                            'position': openapi.Schema(type=openapi.TYPE_STRING),
                            'appliedDate': openapi.Schema(type=openapi.TYPE_STRING),
                            'status': openapi.Schema(type=openapi.TYPE_STRING),
                            'experience': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                )
            )
        }
    )
    def getRecentApplications(self, request):
        opportunities = md.Opportunity.objects.filter(company=request.user)
        applications = app_models.Application.objects.filter(
            opportunities__in=opportunities,
            approve=True
        ).order_by('-createdate')[:5]
        
        data = []
        for app in applications:
            data.append({
                'id': app.id,
                'applicantName': app.student.name if app.student else app.team.name,
                'position': app.opportunities.first().title,
                'appliedDate': app.createdate.isoformat(),
                'status': app.status,
                'experience': app.proposal,
            })
        return Response(data)

    @swagger_auto_schema(
        operation_description="Get all applications for company opportunities",
        responses={
            200: openapi.Response(
                description="List of all applications",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'applicantName': openapi.Schema(type=openapi.TYPE_STRING),
                            'position': openapi.Schema(type=openapi.TYPE_STRING),
                            'appliedDate': openapi.Schema(type=openapi.TYPE_STRING),
                            'status': openapi.Schema(type=openapi.TYPE_STRING),
                            'experience': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                )
            )
        }
    )
    def getAllApplicationsOfCompany(self, request):
        opportunities = md.Opportunity.objects.filter(company=request.user)
        applications = app_models.Application.objects.filter(
            opportunities__in=opportunities,
            approve=True
        ).order_by('-createdate')
        
        data = []
        for app in applications:
            data.append({
                'id': app.id,
                'applicantName': app.student.name if app.student else app.team.name,
                'position': app.opportunities.first().title,
                'appliedDate': app.createdate.isoformat(),
                'status': app.status,
                'experience': app.proposal,
            })
        return Response(data)

    @swagger_auto_schema(
        operation_description="Get applications for a specific opportunity",
        manual_parameters=[
            openapi.Parameter('postId', openapi.IN_PATH, description="Opportunity ID", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: openapi.Response(
                description="List of applications for the opportunity",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'applicantName': openapi.Schema(type=openapi.TYPE_STRING),
                            'position': openapi.Schema(type=openapi.TYPE_STRING),
                            'appliedDate': openapi.Schema(type=openapi.TYPE_STRING),
                            'status': openapi.Schema(type=openapi.TYPE_STRING),
                            'experience': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                )
            )
        }
    )
    def getApplicationByPostId(self, request, postId):
        try:
            opportunity = md.Opportunity.objects.get(id=postId, company=request.user)
            applications = opportunity.applications.all().order_by('-createdate')
            
            data = []
            for app in applications:
                data.append({
                    'id': app.id,
                    'applicantName': app.student.name if app.student else app.team.name,
                    'position': opportunity.title,
                    'appliedDate': app.createdate.isoformat(),
                    'status': app.status,
                    'experience': app.proposal,
                })
            return Response(data)
        except md.Opportunity.DoesNotExist:
            return Response({'error': 'Opportunity not found'}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="Get application chart data for the last 6 months",
        responses={
            200: openapi.Response(
                description="Chart data for applications and jobs",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'month': openapi.Schema(type=openapi.TYPE_STRING),
                            'applications': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'jobs': openapi.Schema(type=openapi.TYPE_INTEGER)
                        }
                    )
                )
            )
        }
    )
    def getApplicationChartData(self, request):
        # Get data for last 6 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)

        # Get monthly application counts
        applications = app_models.Application.objects.filter(
            opportunities__company=request.user,
            createdate__gte=start_date,
            approve=True
        ).annotate(
            month=TruncMonth('createdate')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        # Get monthly job post counts
        jobs = md.Opportunity.objects.filter(
            company=request.user,
            created_at__gte=start_date
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        months = {}
        current = start_date
        while current <= end_date:
            month_key = current.strftime('%Y-%m')
            months[month_key] = {
                'month': current.strftime('%B %Y'),
                'applications': 0,
                'jobs': 0
            }
            current = (current.replace(day=1) + timedelta(days=32)).replace(day=1)

        # Fill in the actual values
        for app in applications:
            month_key = app['month'].strftime('%Y-%m')
            if month_key in months:
                months[month_key]['applications'] = app['count']

        for job in jobs:
            month_key = job['month'].strftime('%Y-%m')
            if month_key in months:
                months[month_key]['jobs'] = job['count']

        return Response(list(months.values()))

    @swagger_auto_schema(
        operation_description="Get status counts for company opportunities and applications",
        responses={
            200: openapi.Response(
                description="Status counts for jobs and applications",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'value': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'thisMonth': openapi.Schema(type=openapi.TYPE_INTEGER)
                        }
                    )
                )
            )
        }
    )
    def getStatusCountOfCompany(self, request):
        # Get current month's start and end dates
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        # Get total job posts
        total_jobs = md.Opportunity.objects.filter(company=request.user).count()
        this_month_jobs = md.Opportunity.objects.filter(
            company=request.user,
            created_at__gte=month_start,
            created_at__lte=month_end
        ).count()

        # Get total applications
        total_applications = app_models.Application.objects.filter(
            opportunities__company=request.user,
            approve=True
        ).count()
        this_month_applications = app_models.Application.objects.filter(
            opportunities__company=request.user,
            createdate__gte=month_start,
            createdate__lte=month_end
        ).count()

        # Get total accepted applications
        total_accepted = app_models.Application.objects.filter(
            opportunities__company=request.user,
            status='accepted'
        ).count()
        this_month_accepted = app_models.Application.objects.filter(
            opportunities__company=request.user,
            status='accepted',
            createdate__gte=month_start,
            createdate__lte=month_end
        ).count()

        return Response([
            {
                'name': 'totalJobPosts',
                'value': total_jobs,
                'thisMonth': this_month_jobs
            },
            {
                'name': 'totalApplications',
                'value': total_applications,
                'thisMonth': this_month_applications
            },
            {
                'name': 'totalAccepted',
                'value': total_accepted,
                'thisMonth': this_month_accepted
            }
        ])

    @swagger_auto_schema(
        operation_description="Get application status distribution for pie chart",
        responses={
            200: openapi.Response(
                description="Application status distribution",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'status': openapi.Schema(type=openapi.TYPE_STRING),
                            'value': openapi.Schema(type=openapi.TYPE_INTEGER)
                        }
                    )
                )
            )
        }
    )
    def getApplicationStatusPieChartData(self, request):
        status_counts = app_models.Application.objects.filter(
            opportunities__company=request.user,
            approve=True
        ).values('status').annotate(
            value=Count('id')
        ).order_by('status')

        return Response([
            {
                'status': item['status'],
                'value': item['value']
            }
            for item in status_counts
        ]) 
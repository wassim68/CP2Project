from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from Auth.serlaizers import UserCompanySerializer, UserStudentSerializer, SkillsSerializer
from post.serializer import opportunity_serializer, team_serializer
from Auth.models import User, Skills
import random

class Command(BaseCommand):
    help = 'Populates the database with sample data using serializers'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to populate database...')
        
        # Create skills
        skills = [
            'Python', 'Django', 'JavaScript', 'React', 'Java', 
            'C++', 'Machine Learning', 'Data Analysis', 'UI/UX Design',
            'Project Management', 'Communication', 'Teamwork'
        ]
        skill_objects = []
        for skill_name in skills:
            serializer = SkillsSerializer(data={'name': skill_name})
            if serializer.is_valid():
                skill = serializer.save()
                skill_objects.append(skill)
                self.stdout.write(f'Created skill: {skill_name}')
            else:
                self.stdout.write(f'Error creating skill {skill_name}: {serializer.errors}')

        # Create companies
        companies_data = [
            {
                'name': 'TechCorp',
                'email': 'info@techcorp.com',
                'password': 'company123',
                'company': {'category': 'CS'},
                'type': 'Company'
            },
            {
                'name': 'HealthCare Inc',
                'email': 'contact@healthcare.com',
                'password': 'company123',
                'company': {'category': 'HL'},
                'type': 'Company'
            },
            {
                'name': 'EduTech Solutions',
                'email': 'support@edutech.com',
                'password': 'company123',
                'company': {'category': 'ED'},
                'type': 'Company'
            },
            {
                'name': 'LegalTech',
                'email': 'info@legaltech.com',
                'password': 'company123',
                'company': {'category': 'LW'},
                'type': 'Company'
            }
        ]

        company_users = []
        for company_data in companies_data:
            serializer = UserCompanySerializer(data=company_data)
            if serializer.is_valid():
                user = serializer.save()
                company_users.append(user)
                self.stdout.write(f'Created company: {company_data["name"]}')
            else:
                self.stdout.write(f'Error creating company {company_data["name"]}: {serializer.errors}')

        # Create students
        students_data = [
            {
                'name': 'John Doe',
                'email': 'john@student.com',
                'password': 'student123',
                'type': 'Student',
                'student': {
                    'gendre': 'M',
                    'category': 'CS',
                    'description': 'Computer Science student',
                    'skill_input': random.sample(skills, 3),
                    'education': [{
                        'degree': 'Bachelor',
                        'institution': 'Tech University',
                        'start': 2020,
                        'end': 2024
                    }],
                    'experience': ['Intern at TechCorp']
                }
            },
            {
                'name': 'Jane Smith',
                'email': 'jane@student.com',
                'password': 'student123',
                'type': 'Student',
                'student': {
                    'gendre': 'F',
                    'category': 'BM',
                    'description': 'Business Management student',
                    'skill_input': random.sample(skills, 3),
                    'education': [{
                        'degree': 'Bachelor',
                        'institution': 'Business School',
                        'start': 2020,
                        'end': 2024
                    }],
                    'experience': ['Marketing Intern']
                }
            },
            {
                'name': 'Alex Johnson',
                'email': 'alex@student.com',
                'password': 'student123',
                'type': 'Student',
                'student': {
                    'gendre': 'P',
                    'category': 'EN',
                    'description': 'Engineering student',
                    'skill_input': random.sample(skills, 3),
                    'education': [{
                        'degree': 'Bachelor',
                        'institution': 'Engineering College',
                        'start': 2020,
                        'end': 2024
                    }],
                    'experience': ['Engineering Intern']
                }
            }
        ]

        student_users = []
        for student_data in students_data:
            serializer = UserStudentSerializer(data=student_data)
            if serializer.is_valid():
                user = serializer.save()
                student_users.append(user)
                self.stdout.write(f'Created student: {student_data["name"]}')
            else:
                self.stdout.write(f'Error creating student {student_data["name"]}: {serializer.errors}')

        # Create opportunities
        opportunity_types = ['internship', 'Problem']
        work_types = ['Online', 'Onsite', 'Hybrid']
        
        for company in company_users:
            for opp_type in opportunity_types:
                opportunity_data = {
                    'title': f'{company.name} {opp_type} Opportunity',
                    'description': f'This is a sample {opp_type} opportunity from {company.name}',
                    'Type': opp_type,
                    'category': company.company.category,
                    'worktype': random.choice(work_types),
                    'endday': timezone.now() + timedelta(days=30),
                    'duration': random.randint(1, 6),
                    'skill_input': random.sample(skills, 3),
                    'company': company.id
                }
                
                serializer = opportunity_serializer(data=opportunity_data)
                if serializer.is_valid():
                    opportunity = serializer.save()
                    self.stdout.write(f'Created opportunity: {opportunity.title}')
                else:
                    self.stdout.write(f'Error creating opportunity: {serializer.errors}')

        # Create teams
        team_categories = ['project', 'study', 'research', 'hackathon']
        
        for i in range(3):
            leader = random.choice(student_users)
            other_students = [s for s in student_users if s != leader]
            team_data = {
                'name': f'Team {i+1}',
                'description': f'This is team {i+1} working on a {team_categories[i]}',
                'category': team_categories[i],
                'leader_id': leader.id,
                'student_ids': [s.id for s in random.sample(other_students, min(2, len(other_students)))]
            }
            
            serializer = team_serializer(data=team_data)
            if serializer.is_valid():
                team = serializer.save()
                self.stdout.write(f'Created team: {team.name}')
            else:
                self.stdout.write(f'Error creating team: {serializer.errors}')

        self.stdout.write(self.style.SUCCESS('Successfully populated the database!')) 
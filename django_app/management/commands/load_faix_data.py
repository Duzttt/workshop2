"""
Management command to load FAIX data from JSON files into the database.
"""

import json
import logging
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction

from django_app.models import (
    FacultyInfo, VisionMission, Programme, Admission, Department,
    Facility, AcademicResource, ResearchFocus, CourseInfo,
    TopManagement, KeyHighlight, FAQ, ScheduleData
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Load FAIX data from JSON files into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-dir',
            type=str,
            default='data/separated',
            help='Directory containing JSON data files (default: data/separated)'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing data before loading'
        )

    def handle(self, *args, **options):
        data_dir = Path(options['data_dir'])
        clear_existing = options['clear_existing']

        self.stdout.write(self.style.SUCCESS(f'Loading FAIX data from {data_dir}'))

        if clear_existing:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_existing_data()

        # Load each JSON file
        json_files = [
            'faculty_info.json',
            'vision_mission.json',
            'programmes.json',
            'admission.json',
            'departments.json',
            'facilities.json',
            'academic_resources.json',
            'research_focus.json',
            'course_info.json',
            'top_management.json',
            'key_highlights.json',
            'faqs.json',
            'schedule.json',
        ]

        for json_file in json_files:
            file_path = data_dir / json_file
            if file_path.exists():
                self.stdout.write(f'Loading {json_file}...')
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.load_data(json_file, data)
                    self.stdout.write(self.style.SUCCESS(f'  [OK] Loaded {json_file}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  [ERROR] Error loading {json_file}: {e}'))
                    logger.error(f'Error loading {json_file}: {e}', exc_info=True)
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠ File not found: {json_file}'))

        self.stdout.write(self.style.SUCCESS('\nFAIX data loading complete!'))

    def clear_existing_data(self):
        """Clear all FAIX data from database"""
        with transaction.atomic():
            FacultyInfo.objects.all().delete()
            VisionMission.objects.all().delete()
            Programme.objects.all().delete()
            Admission.objects.all().delete()
            Department.objects.all().delete()
            Facility.objects.all().delete()
            AcademicResource.objects.all().delete()
            ResearchFocus.objects.all().delete()
            CourseInfo.objects.all().delete()
            TopManagement.objects.all().delete()
            KeyHighlight.objects.all().delete()
            FAQ.objects.all().delete()
            ScheduleData.objects.all().delete()

    def load_data(self, filename, data):
        """Load data based on filename"""
        with transaction.atomic():
            if filename == 'faculty_info.json':
                self.load_faculty_info(data)
            elif filename == 'vision_mission.json':
                self.load_vision_mission(data)
            elif filename == 'programmes.json':
                self.load_programmes(data)
            elif filename == 'admission.json':
                self.load_admission(data)
            elif filename == 'departments.json':
                self.load_departments(data)
            elif filename == 'facilities.json':
                self.load_facilities(data)
            elif filename == 'academic_resources.json':
                self.load_academic_resources(data)
            elif filename == 'research_focus.json':
                self.load_research_focus(data)
            elif filename == 'course_info.json':
                self.load_course_info(data)
            elif filename == 'top_management.json':
                self.load_top_management(data)
            elif filename == 'key_highlights.json':
                self.load_key_highlights(data)
            elif filename == 'faqs.json':
                self.load_faqs(data)
            elif filename == 'schedule.json':
                self.load_schedule(data)

    def load_faculty_info(self, data):
        """Load faculty information"""
        if 'faculty_info' not in data:
            return
        
        info = data['faculty_info']
        FacultyInfo.objects.update_or_create(
            name=info.get('name', ''),
            defaults={
                'university': info.get('university', ''),
                'established': info.get('established', ''),
                'dean': info.get('dean', ''),
                'academic_staff_count': info.get('staff_count', {}).get('academic', 0),
                'administrative_staff_count': info.get('staff_count', {}).get('administrative', 0),
                'address_street': info.get('address', {}).get('street', ''),
                'address_postcode': info.get('address', {}).get('postcode', ''),
                'address_city': info.get('address', {}).get('city', ''),
                'address_state': info.get('address', {}).get('state', ''),
                'address_country': info.get('address', {}).get('country', ''),
                'contact_email': info.get('contact', {}).get('email', ''),
                'contact_phone': info.get('contact', {}).get('phone', ''),
                'contact_website': info.get('contact', {}).get('website', ''),
            }
        )

    def load_vision_mission(self, data):
        """Load vision and mission"""
        if 'vision_mission' not in data:
            return
        
        vm = data['vision_mission']
        VisionMission.objects.create(
            vision=vm.get('vision', ''),
            mission=vm.get('mission', []),
            objectives=vm.get('objectives', []),
        )

    def load_programmes(self, data):
        """Load programmes"""
        if 'programmes' not in data:
            return
        
        programs = data['programmes']
        
        # Load undergraduate programmes
        for prog in programs.get('undergraduate', []):
            Programme.objects.create(
                name=prog.get('name', ''),
                code=prog.get('code', ''),
                programme_type='undergraduate',
                duration=prog.get('duration', ''),
                focus_areas=prog.get('focus_areas', []),
                career_opportunities=prog.get('career_opportunities', []),
                learning_distribution=prog.get('learning_distribution', {}),
                graduate_attributes=prog.get('graduate_attributes', []),
            )
        
        # Load postgraduate programmes
        for prog in programs.get('postgraduate', []):
            Programme.objects.create(
                name=prog.get('name', ''),
                code=prog.get('code', ''),
                programme_type='postgraduate',
                programme_focus=prog.get('focus', ''),
                programme_format=prog.get('type', ''),
            )

    def load_admission(self, data):
        """Load admission information"""
        if 'admission' not in data:
            return
        
        admission = data['admission']
        
        # Load undergraduate local
        if 'undergraduate_local' in admission:
            local = admission['undergraduate_local']
            Admission.objects.create(
                admission_type='undergraduate_local',
                requirements=local.get('requirements', {}),
                application_links=local.get('application_links', {}),
            )
        
        # Load undergraduate international
        if 'undergraduate_international' in admission:
            intl = admission['undergraduate_international']
            Admission.objects.create(
                admission_type='undergraduate_international',
                requirements=intl.get('requirements', {}),
                application_links=intl.get('application_links', {}),
                learning_approach=intl.get('learning_approach', ''),
            )
        
        # Load postgraduate
        if 'postgraduate' in admission:
            pg = admission['postgraduate']
            Admission.objects.create(
                admission_type='postgraduate',
                requirements=pg.get('entry_requirements', []),
                language_requirements=pg.get('language_requirements', {}),
                contact_info=pg.get('contact', {}),
            )

    def load_departments(self, data):
        """Load departments"""
        if 'departments' not in data:
            return
        
        for dept in data['departments']:
            Department.objects.create(
                name=dept.get('name', ''),
                focus=dept.get('focus', ''),
            )

    def load_facilities(self, data):
        """Load facilities"""
        if 'facilities' not in data:
            return
        
        facilities = data['facilities']
        
        # Load available facilities
        for facility_name in facilities.get('available', []):
            Facility.objects.create(
                name=facility_name,
                facility_type='general',
                description=facility_name,
                booking_url=facilities.get('booking_system', ''),
            )
        
        # Load AI labs
        for lab in facilities.get('laboratories', {}).get('ai_labs', []):
            Facility.objects.create(
                name=lab.get('name', ''),
                facility_type='AI Laboratory',
                block=lab.get('block', ''),
                level=lab.get('level', ''),
            )
        
        # Load Cybersecurity labs
        for lab in facilities.get('laboratories', {}).get('cybersec_labs', []):
            Facility.objects.create(
                name=lab.get('name', ''),
                facility_type='Cybersecurity Laboratory',
                block=lab.get('block', ''),
                level=lab.get('level', ''),
            )

    def load_academic_resources(self, data):
        """Load academic resources"""
        if 'academic_resources' not in data:
            return
        
        resources = data['academic_resources']
        
        # Load ulearn portal
        if 'ulearn_portal' in resources:
            AcademicResource.objects.create(
                name='uLearn Portal',
                resource_type='Portal',
                url=resources.get('ulearn_portal', ''),
                description='Online learning portal for FAIX students',
            )
        
        # Load resource list
        if 'resources' in resources:
            for resource_name in resources.get('resources', []):
                AcademicResource.objects.create(
                    name=resource_name,
                    resource_type='Resource',
                    description=resource_name,
                )

    def load_research_focus(self, data):
        """Load research focus areas"""
        if 'research_focus' not in data:
            return
        
        for focus in data['research_focus']:
            ResearchFocus.objects.create(
                name=focus,
                description=focus,
            )

    def load_course_info(self, data):
        """Load course information"""
        if 'course_info' not in data:
            return
        
        for course in data['course_info']:
            CourseInfo.objects.create(
                name=course.get('name', ''),
                code=course.get('code', ''),
                description=course.get('description', ''),
                category=course.get('category', ''),
            )

    def load_top_management(self, data):
        """Load top management information"""
        if 'top_management' not in data:
            return
        
        for person in data['top_management']:
            TopManagement.objects.create(
                name=person.get('name', ''),
                position=person.get('position', ''),
                title=person.get('title', ''),
                email=person.get('email', ''),
                keywords=person.get('keywords', []),
            )

    def load_key_highlights(self, data):
        """Load key highlights"""
        if 'key_highlights' not in data:
            return
        
        for highlight in data['key_highlights']:
            KeyHighlight.objects.create(
                highlight=highlight,
            )

    def load_faqs(self, data):
        """Load FAQs"""
        if 'faqs' not in data:
            return
        
        for faq in data['faqs']:
            FAQ.objects.create(
                question=faq.get('question', ''),
                answer=faq.get('answer', ''),
                category=faq.get('category', ''),
            )

    def load_schedule(self, data):
        """Load schedule data"""
        if 'schedule' not in data:
            return
        
        for item in data['schedule']:
            ScheduleData.objects.create(
                title=item.get('title', ''),
                description=item.get('description', ''),
                time=item.get('time', ''),
                category=item.get('category', ''),
            )

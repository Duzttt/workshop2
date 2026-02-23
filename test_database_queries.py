#!/usr/bin/env python
"""
Test script to verify database queries work correctly.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')
import django
django.setup()

from django_app.models import (
    FacultyInfo, VisionMission, Programme, Admission, Department,
    Facility, AcademicResource, ResearchFocus, CourseInfo,
    TopManagement, KeyHighlight, FAQ, ScheduleData
)


def test_database_queries():
    """Test database queries for FAIX data."""
    print("=" * 60)
    print("Testing Database Queries")
    print("=" * 60)
    
    # Test 1: Faculty Info
    print("\n1. Testing Faculty Info...")
    try:
        faculty = FacultyInfo.objects.first()
        if faculty:
            print(f"   [OK] Faculty: {faculty.name}")
            print(f"   [OK] Dean: {faculty.dean}")
            print(f"   [OK] Established: {faculty.established}")
        else:
            print("   [ERROR] No faculty data found!")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 2: Vision & Mission
    print("\n2. Testing Vision & Mission...")
    try:
        vm = VisionMission.objects.first()
        if vm:
            print(f"   [OK] Vision: {vm.vision[:100]}...")
            print(f"   [OK] Mission statements: {len(vm.mission)}")
            print(f"   [OK] Objectives: {len(vm.objectives)}")
        else:
            print("   [ERROR] No vision/mission data found!")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 3: Programmes
    print("\n3. Testing Programmes...")
    try:
        undergrad = Programme.objects.filter(programme_type='undergraduate')
        postgrad = Programme.objects.filter(programme_type='postgraduate')
        print(f"   [OK] Undergraduate programmes: {len(undergrad)}")
        for prog in undergrad:
            print(f"     - {prog.code}: {prog.name}")
        print(f"   [OK] Postgraduate programmes: {len(postgrad)}")
        for prog in postgrad:
            print(f"     - {prog.code}: {prog.name}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 4: Admission
    print("\n4. Testing Admission...")
    try:
        admissions = Admission.objects.all()
        print(f"   [OK] Admission types: {len(admissions)}")
        for adm in admissions:
            print(f"     - {adm.admission_type}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 5: Departments
    print("\n5. Testing Departments...")
    try:
        departments = Department.objects.all()
        print(f"   [OK] Departments: {len(departments)}")
        for dept in departments:
            print(f"     - {dept.name}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 6: Facilities
    print("\n6. Testing Facilities...")
    try:
        facilities = Facility.objects.all()
        print(f"   [OK] Facilities: {len(facilities)}")
        for facility in facilities[:5]:
            print(f"     - {facility.name} ({facility.facility_type})")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 7: Academic Resources
    print("\n7. Testing Academic Resources...")
    try:
        resources = AcademicResource.objects.all()
        print(f"   [OK] Academic Resources: {len(resources)}")
        for resource in resources:
            print(f"     - {resource.name}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 8: Research Focus
    print("\n8. Testing Research Focus...")
    try:
        research = ResearchFocus.objects.all()
        print(f"   [OK] Research Focus Areas: {len(research)}")
        for focus in research:
            print(f"     - {focus.name}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 9: Top Management
    print("\n9. Testing Top Management...")
    try:
        management = TopManagement.objects.all()
        print(f"   [OK] Top Management: {len(management)}")
        for person in management[:5]:
            print(f"     - {person.name} ({person.position})")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 10: Key Highlights
    print("\n10. Testing Key Highlights...")
    try:
        highlights = KeyHighlight.objects.all()
        print(f"   [OK] Key Highlights: {len(highlights)}")
        for highlight in highlights[:3]:
            print(f"     - {highlight.highlight[:80]}...")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 11: FAQs
    print("\n11. Testing FAQs...")
    try:
        faqs = FAQ.objects.all()
        print(f"   [OK] FAQs: {len(faqs)}")
        for faq in faqs[:3]:
            print(f"     - Q: {faq.question[:60]}...")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 12: Schedule Data
    print("\n12. Testing Schedule Data...")
    try:
        schedule = ScheduleData.objects.all()
        print(f"   [OK] Schedule items: {len(schedule)}")
        for item in schedule[:5]:
            print(f"     - {item.title}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Test 13: Query by specific intent (simulating chatbot queries)
    print("\n13. Testing Chatbot-style Queries...")
    try:
        # Query for dean
        faculty = FacultyInfo.objects.first()
        if faculty and faculty.dean:
            print(f"   [OK] Dean query: {faculty.dean}")
        
        # Query for programs
        programs = Programme.objects.all()
        if programs:
            print(f"   [OK] Programs query: {len(programs)} programs found")
        
        # Query for staff by department
        management = TopManagement.objects.filter(position__icontains='dean')
        if management:
            print(f"   [OK] Dean query (from TopManagement): {len(management)} found")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    print("\n" + "=" * 60)
    print("Database Query Test Complete!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_database_queries()
    sys.exit(0 if success else 1)

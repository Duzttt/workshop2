"""
Knowledge Base module that uses Django database instead of JSON files.
This is the database-backed version of the knowledge base.
"""

import logging
from typing import Optional, Dict, Any, List
from django.db.models import Q

# Import Django models
try:
    from django_app.models import (
        FacultyInfo, VisionMission, Programme, Admission, Department,
        Facility, AcademicResource, ResearchFocus, CourseInfo,
        TopManagement, KeyHighlight, FAQ, ScheduleData
    )
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    logging.getLogger("faix_chatbot").warning("Django models not available")

logger = logging.getLogger(__name__)


class KnowledgeBaseDB:
    """
    Knowledge Base module that retrieves answers from FAIX database.
    Uses Django ORM for efficient data retrieval.
    """
    
    def __init__(self):
        """
        Initialize KnowledgeBaseDB.
        """
        if not DJANGO_AVAILABLE:
            raise ImportError("Django models not available. Cannot use database knowledge base.")
        
        logger.info("KnowledgeBaseDB initialized with database backend")
    
    def get_answer(self, intent: str, user_text: str) -> Optional[str]:
        """
        Get answer from database based on intent and user text.
        
        Args:
            intent: The detected intent
            user_text: The user's query text
            
        Returns:
            Answer string or None if not found
        """
        if not DJANGO_AVAILABLE:
            return None
        
        intent = intent.lower() if intent else ""
        user_lower = user_text.lower() if user_text else ""
        
        # Priority 1: Check for specific keywords in user text
        # Top management queries
        if any(kw in user_lower for kw in ['nc', 'vc', 'dvc', 'avc', 'chancellor', 'canselor', 
                                            'vice chancellor', 'deputy vice chancellor', 'assistant vice chancellor',
                                            'treasurer', 'bendahari', 'librarian', 'pustakawan', 'ketua pegawai',
                                            'top management', 'pengurusan tertinggi']):
            return self._get_top_management_answer(user_text)
        
        # Staff member queries
        staff_keywords = ['dr.', 'doctor', 'professor', 'associate professor', 'lecturer', 'senior lecturer', 'ts. dr.', 'ts dr']
        has_staff_keyword = any(kw in user_lower for kw in staff_keywords)
        
        # Check if query might contain a staff name
        words = [w.strip().strip('.,!?') for w in user_text.split() if len(w.strip()) > 2]
        has_name_like_words = len([w for w in words if w[0].isupper() and w.lower() not in ['who', 'what', 'when', 'where', 'why', 'how', 'is', 'are', 'the', 'for', 'contact', 'info', 'information']]) >= 1
        
        if has_staff_keyword or has_name_like_words:
            staff_answer = self._get_staff_by_name(user_text)
            if staff_answer:
                return staff_answer
        
        # Dean queries
        if any(kw in user_lower for kw in ['who is dean', 'who is the dean', 'dean', 'head of faculty']) and 'chancellor' not in user_lower:
            faculty = FacultyInfo.objects.first()
            if faculty and faculty.dean:
                return f"The Dean of FAIX is **{faculty.dean}**."
        
        # BCSAI/BCSCS program code queries
        if any(kw in user_lower for kw in ['baxi', 'baxz', 'mcsss', 'mtdsa']):
            return self._get_program_answer(user_text)
        
        # Map intents to database queries
        if intent == 'about_faix':
            return self._get_about_faix_answer(user_text)
        elif intent == 'program_info':
            return self._get_program_answer(user_text)
        elif intent == 'admission':
            return self._get_admission_answer(user_text)
        elif intent == 'fees':
            return self._get_fees_answer(user_text)
        elif intent == 'career':
            return self._get_career_answer(user_text)
        elif intent == 'facility_info':
            return self._get_facility_answer(user_text)
        elif intent == 'academic_resources':
            return self._get_academic_resources_answer(user_text)
        elif intent == 'research':
            return self._get_research_answer(user_text)
        elif intent == 'staff_contact':
            if any(kw in user_lower for kw in ['dean', 'head', 'leader']):
                faculty = FacultyInfo.objects.first()
                if faculty and faculty.dean:
                    return f"The Dean of FAIX is **{faculty.dean}**."
            return self._get_contact_answer(user_text)
        elif intent == 'academic_schedule':
            return self._get_schedule_answer(user_text)
        
        # Check FAQs in database
        return self._search_faix_faqs(user_lower)
    
    def _get_top_management_answer(self, user_text: str) -> Optional[str]:
        """Get answer about top management (VC, NC, etc.)"""
        user_lower = user_text.lower()
        
        # Check for specific person queries
        top_management = TopManagement.objects.all()
        
        for person in top_management:
            keywords = person.keywords
            if keywords:
                for keyword in keywords:
                    keyword_lower = keyword.lower().strip()
                    if keyword_lower in user_lower:
                        # Found matching person
                        answer = f"**{person.name}**\n\n"
                        answer += f"- **Position:** {person.position}\n"
                        if person.title:
                            answer += f"- **Title:** {person.title}\n"
                        if person.email:
                            answer += f"- **Email:** {person.email}\n"
                        return answer
        
        # Check for position queries
        if 'dean' in user_lower:
            faculty = FacultyInfo.objects.first()
            if faculty and faculty.dean:
                return f"The Dean of FAIX is **{faculty.dean}**."
        
        return None
    
    def _get_staff_by_name(self, user_text: str) -> Optional[str]:
        """Get staff information by name"""
        user_lower = user_text.lower()
        
        # Check top management first
        top_management = TopManagement.objects.all()
        for person in top_management:
            name_lower = person.name.lower()
            if name_lower in user_lower or any(kw in user_lower for kw in person.keywords):
                answer = f"**{person.name}**\n\n"
                answer += f"- **Position:** {person.position}\n"
                if person.title:
                    answer += f"- **Title:** {person.title}\n"
                if person.email:
                    answer += f"- **Email:** {person.email}\n"
                return answer
        
        return None
    
    def _get_about_faix_answer(self, user_text: str) -> Optional[str]:
        """Get answer about FAIX faculty info, vision, mission, etc."""
        user_lower = user_text.lower()
        
        # Vision
        if 'vision' in user_lower:
            vm = VisionMission.objects.first()
            if vm and vm.vision:
                return f"**FAIX Vision:**\n\n{vm.vision}"
        
        # Mission
        if 'mission' in user_lower:
            vm = VisionMission.objects.first()
            if vm and vm.mission:
                if isinstance(vm.mission, list):
                    mission_text = '\n'.join([f"- {item}" for item in vm.mission])
                    return f"**FAIX Mission:**\n\n{mission_text}"
                else:
                    return f"**FAIX Mission:**\n\n{vm.mission}"
        
        # Objectives
        if 'objective' in user_lower or 'objectives' in user_lower:
            vm = VisionMission.objects.first()
            if vm and vm.objectives:
                if isinstance(vm.objectives, list):
                    obj_text = '\n'.join([f"- {item}" for item in vm.objectives])
                    return f"**FAIX Objectives:**\n\n{obj_text}"
        
        # Departments
        if 'department' in user_lower:
            departments = Department.objects.all()
            if departments:
                dept_list = '\n'.join([f"- **{dept.name}**: {dept.focus}" for dept in departments])
                return f"**FAIX Departments:**\n\n{dept_list}"
        
        # Highlights
        if 'highlight' in user_lower or 'key' in user_lower or 'special' in user_lower:
            highlights = KeyHighlight.objects.all()
            if highlights:
                hl_list = '\n'.join([f"- {hl.highlight}" for hl in highlights[:5]])
                return f"**Key Highlights of FAIX:**\n\n{hl_list}"
        
        # General about FAIX
        faculty = FacultyInfo.objects.first()
        if not faculty:
            return None
        
        answer = f"**{faculty.name}**\n\n"
        answer += f"- **University:** {faculty.university}\n"
        if faculty.established:
            answer += f"- **Established:** {faculty.established}\n"
        if faculty.dean:
            answer += f"- **Dean:** {faculty.dean}\n"
        
        vm = VisionMission.objects.first()
        if vm and vm.vision:
            answer += f"\n**Vision:** {vm.vision}"
        
        return answer
    
    def _get_program_answer(self, user_text: str) -> Optional[str]:
        """Get answer about programmes offered"""
        user_lower = user_text.lower()
        
        # Check for specific program codes
        if 'baxi' in user_lower:
            program = Programme.objects.filter(code__iexact='BAXI').first()
            if program:
                return self._format_program_details(program)
        
        if 'baxz' in user_lower:
            program = Programme.objects.filter(code__iexact='BAXZ').first()
            if program:
                return self._format_program_details(program)
        
        if 'mcsss' in user_lower:
            program = Programme.objects.filter(code__iexact='MCSSS').first()
            if program:
                return self._format_program_details(program)
        
        if 'mtdsa' in user_lower:
            program = Programme.objects.filter(code__icontains='MTDSA').first()
            if program:
                return self._format_program_details(program)
        
        # Check for specific program keywords
        if any(kw in user_lower for kw in ['artificial intelligence', 'ai programme', 'ai program', 'ai degree']):
            program = Programme.objects.filter(name__icontains='Artificial Intelligence').first()
            if program:
                return self._format_program_details(program)
        
        if any(kw in user_lower for kw in ['security', 'cyber', 'computer security']):
            program = Programme.objects.filter(name__icontains='Security').first()
            if program:
                return self._format_program_details(program)
        
        # Postgraduate programs
        if any(kw in user_lower for kw in ['master', 'postgraduate', 'graduate']):
            postgrad = Programme.objects.filter(programme_type='postgraduate')
            if postgrad:
                prog_list = []
                for prog in postgrad:
                    prog_list.append(f"- **{prog.name}** ({prog.code})\n  - Type: {prog.programme_format}\n  - Focus: {prog.programme_focus}")
                return f"**Postgraduate Programmes at FAIX:**\n\n" + '\n'.join(prog_list)
        
        # Undergraduate programs
        if any(kw in user_lower for kw in ['undergraduate', 'bachelor', 'degree']):
            undergrad = Programme.objects.filter(programme_type='undergraduate')
            if undergrad:
                prog_list = []
                for prog in undergrad:
                    focus_hint = ""
                    if 'artificial intelligence' in prog.name.lower():
                        focus_hint = "AI and Machine Learning"
                    elif 'security' in prog.name.lower():
                        focus_hint = "Cybersecurity"
                    elif prog.focus_areas:
                        focus_hint = prog.focus_areas[0] if prog.focus_areas else ""
                    
                    prog_list.append(f"- **{prog.name}** ({prog.code}) - {prog.duration} - Focus: {focus_hint}")
                
                return f"**Undergraduate Programmes at FAIX:**\n\n" + '\n'.join(prog_list) + "\n\n💡 Ask about a specific program (e.g., 'Tell me about BAXI' or 'What is BAXZ?') for more details."
        
        # General programs listing
        undergrad = Programme.objects.filter(programme_type='undergraduate')
        postgrad = Programme.objects.filter(programme_type='postgraduate')
        
        answer = "**Programmes Offered at FAIX:**\n\n"
        if undergrad:
            answer += "**Undergraduate:**\n"
            for prog in undergrad:
                answer += f"- {prog.name} ({prog.code})\n"
        if postgrad:
            answer += "\n**Postgraduate:**\n"
            for prog in postgrad:
                answer += f"- {prog.name} ({prog.code})\n"
        
        return answer
    
    def _format_program_details(self, program: Programme) -> str:
        """Format detailed program information"""
        answer = f"**{program.name}** ({program.code})\n\n"
        if program.duration:
            answer += f"- **Duration:** {program.duration}\n"
        if program.focus_areas:
            answer += f"- **Focus Areas:** {', '.join(program.focus_areas[:5])}\n"
        if program.learning_distribution:
            dist = program.learning_distribution
            coursework = dist.get('coursework', '')
            practical = dist.get('practical_projects', '')
            if coursework or practical:
                answer += f"- **Learning:** {coursework} coursework, {practical} practical\n"
        if program.career_opportunities:
            careers = program.career_opportunities[:5]
            answer += f"\n**Career Opportunities:** {', '.join(careers)}"
        return answer
    
    def _get_admission_answer(self, user_text: str) -> Optional[str]:
        """Get admission requirements information"""
        user_lower = user_text.lower()
        
        if any(kw in user_lower for kw in ['international', 'foreign', 'overseas']):
            adm = Admission.objects.filter(admission_type='undergraduate_international').first()
            if adm:
                answer = "**International Student Admission:**\n\n"
                reqs = adm.requirements
                if isinstance(reqs, dict):
                    for key, value in reqs.items():
                        answer += f"- **{key.replace('_', ' ').title()}:** {value}\n"
                if adm.learning_approach:
                    answer += f"\n**Learning Approach:** {adm.learning_approach}"
                return answer
        
        if any(kw in user_lower for kw in ['postgraduate', 'master']):
            adm = Admission.objects.filter(admission_type='postgraduate').first()
            if adm:
                answer = "**Postgraduate Admission:**\n\n"
                reqs = adm.requirements
                if isinstance(reqs, list):
                    for req in reqs:
                        if isinstance(req, dict):
                            category = req.get('category', '')
                            requirement = req.get('requirement', '')
                            answer += f"- **{category}:** {requirement}\n"
                lang_reqs = adm.language_requirements
                if lang_reqs:
                    answer += f"\n**Language Requirements:**\n"
                    for key, value in lang_reqs.items():
                        answer += f"- **{key.upper()}:** {value}\n"
                return answer
        
        # Default: undergraduate local
        adm = Admission.objects.filter(admission_type='undergraduate_local').first()
        if adm:
            answer = "**Undergraduate Admission (Local):**\n\n"
            reqs = adm.requirements
            if isinstance(reqs, dict):
                for key, value in reqs.items():
                    answer += f"- **{key.replace('_', ' ').title()}:** {value}\n"
            return answer
        
        return None
    
    def _get_fees_answer(self, user_text: str) -> Optional[str]:
        """Get fee information"""
        # Fee information is typically in admission data
        adm = Admission.objects.filter(admission_type='undergraduate_local').first()
        if adm and adm.application_links:
            links = adm.application_links
            if isinstance(links, dict) and 'fees' in links:
                return f"**Fee Schedule:**\n\n{links['fees']}"
        
        # Fallback: return general fee info
        return "**Fee Information:**\n\nFor detailed fee schedules and payment information, please visit: https://bendahari.utem.edu.my/ms/jadual-yuran-pelajar.html"
    
    def _get_career_answer(self, user_text: str) -> Optional[str]:
        """Get career opportunities information"""
        user_lower = user_text.lower()
        
        # Check for specific program career info
        if 'baxi' in user_lower or 'artificial intelligence' in user_lower:
            program = Programme.objects.filter(code__iexact='BAXI').first()
            if program and program.career_opportunities:
                careers = program.career_opportunities
                career_list = '\n'.join([f"- {career}" for career in careers])
                return f"**Career Opportunities for BAXI Graduates:**\n\n{career_list}"
        
        if 'baxz' in user_lower or 'security' in user_lower or 'cyber' in user_lower:
            program = Programme.objects.filter(code__iexact='BAXZ').first()
            if program and program.career_opportunities:
                careers = program.career_opportunities
                career_list = '\n'.join([f"- {career}" for career in careers])
                return f"**Career Opportunities for BAXZ Graduates:**\n\n{career_list}"
        
        # General career info
        programs = Programme.objects.all()
        if programs:
            answer = "**Career Opportunities at FAIX:**\n\n"
            for prog in programs:
                if prog.career_opportunities:
                    careers = prog.career_opportunities[:3]
                    answer += f"**{prog.name}:** {', '.join(careers)}\n\n"
            return answer
        
        return None
    
    def _get_facility_answer(self, user_text: str) -> Optional[str]:
        """Get facility information"""
        user_lower = user_text.lower()
        
        # Check for specific facility types
        if 'lab' in user_lower or 'laboratory' in user_lower:
            labs = Facility.objects.filter(facility_type__icontains='Laboratory')
            if labs:
                lab_list = '\n'.join([f"- **{lab.name}** ({lab.facility_type}) - {lab.block} {lab.level}" for lab in labs])
                return f"**Laboratory Facilities at FAIX:**\n\n{lab_list}"
        
        if 'booking' in user_lower or 'room' in user_lower:
            facility = Facility.objects.filter(facility_type='general', name__icontains='booking').first()
            if facility and facility.booking_url:
                return f"**Room Booking System:**\n\n{facility.booking_url}"
        
        # General facilities
        facilities = Facility.objects.all()
        if facilities:
            facility_list = '\n'.join([f"- **{fac.name}** ({fac.facility_type})" for fac in facilities[:10]])
            return f"**Facilities at FAIX:**\n\n{facility_list}"
        
        return None
    
    def _get_academic_resources_answer(self, user_text: str) -> Optional[str]:
        """Get academic resources information"""
        resources = AcademicResource.objects.all()
        if resources:
            resource_list = '\n'.join([f"- **{res.name}**: {res.url}" for res in resources if res.url])
            return f"**Academic Resources at FAIX:**\n\n{resource_list}"
        
        return None
    
    def _get_research_answer(self, user_text: str) -> Optional[str]:
        """Get research focus information"""
        research = ResearchFocus.objects.all()
        if research:
            research_list = '\n'.join([f"- {focus.name}" for focus in research])
            return f"**Research Focus Areas at FAIX:**\n\n{research_list}"
        
        return None
    
    def _get_contact_answer(self, user_text: str) -> Optional[str]:
        """Get contact information"""
        faculty = FacultyInfo.objects.first()
        if faculty:
            answer = "**FAIX Contact Information:**\n\n"
            if faculty.contact_email:
                answer += f"- **Email:** {faculty.contact_email}\n"
            if faculty.contact_phone:
                answer += f"- **Phone:** {faculty.contact_phone}\n"
            if faculty.contact_website:
                answer += f"- **Website:** {faculty.contact_website}\n"
            return answer
        
        return None
    
    def _get_schedule_answer(self, user_text: str) -> Optional[str]:
        """Get schedule information"""
        schedule = ScheduleData.objects.all()
        if schedule:
            # Get unique categories
            categories = set(schedule.values_list('category', flat=True))
            if categories:
                answer = "**Academic Schedule:**\n\n"
                for category in sorted(categories):
                    items = schedule.filter(category=category)[:5]
                    if items:
                        answer += f"**{category}:**\n"
                        for item in items:
                            answer += f"- {item.title}"
                            if item.time:
                                answer += f" ({item.time})"
                            answer += "\n"
                        answer += "\n"
                return answer
        
        return None
    
    def _search_faix_faqs(self, user_text: str) -> Optional[str]:
        """Search FAQs in database"""
        faqs = FAQ.objects.filter(question__icontains=user_text)
        if faqs:
            faq = faqs.first()
            return f"**Q:** {faq.question}\n\n**A:** {faq.answer}"
        
        # Try to find any FAQ that matches
        faqs = FAQ.objects.all()
        for faq in faqs:
            if user_text in faq.question.lower():
                return f"**Q:** {faq.question}\n\n**A:** {faq.answer}"
        
        return None
    
    def get_documents(self, intent: str, user_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve documents for RAG (Retrieval-Augmented Generation).
        
        Args:
            intent: The detected intent
            user_text: The user's query text
            top_k: Number of documents to retrieve
            
        Returns:
            List of document dictionaries
        """
        documents = []
        
        # Get answer from database
        answer = self.get_answer(intent, user_text)
        if answer:
            documents.append({
                'content': answer,
                'score': 1.0,
                'source': 'database',
                'intent': intent
            })
        
        # Get related FAQs
        faqs = FAQ.objects.filter(category__icontains=intent)[:top_k]
        for faq in faqs:
            documents.append({
                'content': f"**Q:** {faq.question}\n\n**A:** {faq.answer}",
                'score': 0.8,
                'source': 'faq',
                'intent': faq.category
            })
        
        return documents


# Global instance
_db_instance: Optional[KnowledgeBaseDB] = None


def get_db_knowledge_base() -> KnowledgeBaseDB:
    """
    Get or create a global KnowledgeBaseDB instance.
    
    Returns:
        KnowledgeBaseDB instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = KnowledgeBaseDB()
    return _db_instance

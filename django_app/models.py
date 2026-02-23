from django.db import models
from django.utils import timezone
import uuid


def generate_session_id():
    """Generate a unique session ID"""
    return str(uuid.uuid4())


class UserSession(models.Model):
    """Track user sessions and context"""
    session_id = models.CharField(max_length=100, unique=True, default=generate_session_id)
    user_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    context = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user_id']),
        ]

    def __str__(self):
        return f"Session {self.session_id}"


class Conversation(models.Model):
    """Store conversation sessions"""
    user_id = models.CharField(max_length=100, blank=True, null=True)
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Conversation {self.id} - {self.title or 'Untitled'}"


class Message(models.Model):
    """Store individual messages in conversations"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
        ('system', 'System'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    intent = models.CharField(max_length=50, blank=True, null=True)
    confidence = models.FloatField(default=0.0, null=True, blank=True)
    entities = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
            models.Index(fields=['intent']),
        ]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class FAQEntry(models.Model):
    """Knowledge base entries migrated from CSV/JSON"""
    question = models.TextField()
    answer = models.TextField()
    category = models.CharField(max_length=100, db_index=True)
    keywords = models.TextField(help_text="Comma-separated keywords")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    view_count = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['category', 'question']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = "FAQ Entry"
        verbose_name_plural = "FAQ Entries"

    def __str__(self):
        return f"{self.category}: {self.question[:50]}..."

    def get_keywords_list(self):
        """Return keywords as a list"""
        return [kw.strip().lower() for kw in self.keywords.split(',') if kw.strip()]


class Course(models.Model):
    """Store course information"""
    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.IntegerField(default=3)
    program = models.CharField(max_length=100, blank=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='required_for')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['program']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Staff(models.Model):
    """Store staff contact information"""
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    office = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['department']),
        ]
        verbose_name_plural = "Staff"

    def __str__(self):
        return f"{self.name} - {self.title or 'Staff'}"


class Schedule(models.Model):
    """Store schedule and academic calendar information"""
    SEMESTER_CHOICES = [
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    semester = models.CharField(max_length=20, choices=SEMESTER_CHOICES, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    event_type = models.CharField(max_length=50, blank=True, help_text="e.g., registration, classes, exams")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['semester']),
            models.Index(fields=['start_date']),
            models.Index(fields=['event_type']),
        ]

    def __str__(self):
        return f"{self.title} - {self.semester or 'N/A'}"


class ResponseFeedback(models.Model):
    """Store user feedback on bot responses for reinforcement learning"""
    FEEDBACK_CHOICES = [
        ('good', 'Good'),
        ('bad', 'Bad'),
    ]

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='feedbacks')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=10, choices=FEEDBACK_CHOICES)
    user_message = models.TextField(help_text="The original user message that prompted this response")
    bot_response = models.TextField(help_text="The bot response that received feedback")
    intent = models.CharField(max_length=50, blank=True, null=True, help_text="Detected intent for the user message")
    user_comment = models.TextField(blank=True, null=True, help_text="Optional user comment explaining the feedback")
    session_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['message', 'feedback_type']),
            models.Index(fields=['intent', 'feedback_type']),
            models.Index(fields=['session_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Feedback on Message {self.message.id}: {self.feedback_type}"


# ============================================
# FAIX Data Models
# ============================================

class FacultyInfo(models.Model):
    """Store FAIX faculty information"""
    name = models.CharField(max_length=200, unique=True)
    university = models.CharField(max_length=200)
    established = models.CharField(max_length=100, blank=True)
    dean = models.CharField(max_length=200, blank=True)
    academic_staff_count = models.IntegerField(default=0)
    administrative_staff_count = models.IntegerField(default=0)
    address_street = models.CharField(max_length=200, blank=True)
    address_postcode = models.CharField(max_length=20, blank=True)
    address_city = models.CharField(max_length=100, blank=True)
    address_state = models.CharField(max_length=100, blank=True)
    address_country = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Faculty Information"
        verbose_name_plural = "Faculty Information"

    def __str__(self):
        return self.name


class VisionMission(models.Model):
    """Store FAIX vision, mission, and objectives"""
    vision = models.TextField(blank=True)
    mission = models.JSONField(default=list, help_text="List of mission statements")
    objectives = models.JSONField(default=list, help_text="List of objectives")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vision & Mission"
        verbose_name_plural = "Vision & Mission"

    def __str__(self):
        return "FAIX Vision & Mission"


class Programme(models.Model):
    """Store FAIX programmes (undergraduate and postgraduate)"""
    PROGRAMME_TYPE_CHOICES = [
        ('undergraduate', 'Undergraduate'),
        ('postgraduate', 'Postgraduate'),
    ]
    
    name = models.CharField(max_length=300)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    programme_type = models.CharField(max_length=20, choices=PROGRAMME_TYPE_CHOICES)
    duration = models.CharField(max_length=50, blank=True)
    focus_areas = models.JSONField(default=list, help_text="List of focus areas")
    career_opportunities = models.JSONField(default=list, help_text="List of career opportunities")
    learning_distribution = models.JSONField(default=dict, help_text="Coursework and practical percentages")
    graduate_attributes = models.JSONField(default=list, help_text="List of graduate attributes")
    programme_focus = models.TextField(blank=True, help_text="Focus description for postgraduate")
    programme_format = models.CharField(max_length=50, blank=True, help_text="Coursework/Research/ODL")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['programme_type', 'code']
        indexes = [
            models.Index(fields=['programme_type']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Admission(models.Model):
    """Store admission requirements and information"""
    ADMISSION_TYPE_CHOICES = [
        ('undergraduate_local', 'Undergraduate Local'),
        ('undergraduate_international', 'Undergraduate International'),
        ('postgraduate', 'Postgraduate'),
    ]
    
    admission_type = models.CharField(max_length=30, choices=ADMISSION_TYPE_CHOICES, unique=True)
    requirements = models.JSONField(default=dict, help_text="Admission requirements as JSON")
    application_links = models.JSONField(default=dict, help_text="Links to application resources")
    learning_approach = models.TextField(blank=True, help_text="Learning approach description")
    language_requirements = models.JSONField(default=dict, help_text="Language proficiency requirements")
    contact_info = models.JSONField(default=dict, help_text="Contact information")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Admission Information"
        verbose_name_plural = "Admission Information"

    def __str__(self):
        return f"Admission - {self.get_admission_type_display()}"


class Department(models.Model):
    """Store department information"""
    name = models.CharField(max_length=200, unique=True)
    focus = models.TextField(blank=True, help_text="Department focus area")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Facility(models.Model):
    """Store facility information"""
    name = models.CharField(max_length=200)
    facility_type = models.CharField(max_length=100, blank=True, help_text="e.g., laboratory, research center, room")
    block = models.CharField(max_length=50, blank=True)
    level = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    booking_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['facility_type', 'name']
        indexes = [
            models.Index(fields=['facility_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.facility_type})"


class AcademicResource(models.Model):
    """Store academic resources and links"""
    name = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=100, blank=True, help_text="e.g., handbook, portal, form")
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['resource_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.resource_type})"


class ResearchFocus(models.Model):
    """Store research focus areas"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CourseInfo(models.Model):
    """Store course information from JSON data"""
    name = models.CharField(max_length=300)
    code = models.CharField(max_length=20, db_index=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class TopManagement(models.Model):
    """Store top management information (VC, NC, etc.)"""
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    title = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    keywords = models.JSONField(default=list, help_text="Keywords for matching queries")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position', 'name']
        indexes = [
            models.Index(fields=['position']),
        ]

    def __str__(self):
        return f"{self.name} - {self.position}"


class KeyHighlight(models.Model):
    """Store key highlights of FAIX"""
    highlight = models.TextField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.highlight[:50]


class FAQ(models.Model):
    """Store frequently asked questions"""
    question = models.TextField()
    answer = models.TextField()
    category = models.CharField(max_length=100, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'question']
        indexes = [
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.category}: {self.question[:50]}..."


class ScheduleData(models.Model):
    """Store schedule and academic calendar data from JSON"""
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    time = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'title']
        indexes = [
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.title} ({self.category})"

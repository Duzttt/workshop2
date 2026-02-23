"""
Definitions for conversational agents and simple RAG routing helpers.

Agents represent different specialisations (FAQ, schedule, staff contacts, etc.)
that share the same underlying LLM but use different prompts and context.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import json
from enum import Enum

from .knowledge_base import KnowledgeBase

# Configure logger
logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Enum for supported agent types."""
    FAQ = "faq"
    SCHEDULE = "schedule"
    STAFF = "staff"


class AgentValidationError(Exception):
    """Raised when agent configuration is invalid."""
    pass


@dataclass
class Agent:
    id: str
    display_name: str
    description: str
    system_prompt: str
    default_intent: Optional[str] = None
    max_context_length: int = 4000
    temperature: float = 0.7
    max_tokens: int = 500
    
    def __post_init__(self):
        """Validate agent configuration after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate agent configuration."""
        if not self.id or not self.id.strip():
            raise AgentValidationError("Agent ID cannot be empty")
        
        if not self.display_name or not self.display_name.strip():
            raise AgentValidationError("Agent display name cannot be empty")
        
        if not self.system_prompt or not self.system_prompt.strip():
            raise AgentValidationError("Agent system prompt cannot be empty")
        
        if self.temperature < 0 or self.temperature > 2:
            raise AgentValidationError("Agent temperature must be between 0 and 2")
        
        if self.max_tokens <= 0:
            raise AgentValidationError("Agent max_tokens must be positive")
        
        logger.debug(f"Agent {self.id} validation passed")


class AgentRegistry:
    """In-memory registry of available conversational agents."""

    def __init__(self) -> None:
        self._agents: Dict[str, Agent] = {}
        self._init_default_agents()
        logger.info(f"Initialized AgentRegistry with {len(self._agents)} agents")

    def register(self, agent: Agent) -> None:
        """Register an agent with the registry."""
        try:
            agent.validate()
            self._agents[agent.id] = agent
            logger.info(f"Registered agent: {agent.id} ({agent.display_name})")
        except AgentValidationError as e:
            logger.error(f"Failed to register agent {agent.id}: {e}")
            raise

    def get(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID."""
        agent = self._agents.get(agent_id)
        if agent is None:
            logger.warning(f"Agent {agent_id} not found in registry")
        return agent

    def list_agents(self) -> List[Agent]:
        """List all registered agents."""
        return list(self._agents.values())

    def list_agent_ids(self) -> List[str]:
        """List all registered agent IDs."""
        return list(self._agents.keys())

    def validate_all(self) -> bool:
        """Validate all registered agents."""
        try:
            for agent_id, agent in self._agents.items():
                agent.validate()
            logger.info(f"All {len(self._agents)} agents validated successfully")
            return True
        except Exception as e:
            logger.error(f"Agent validation failed: {e}")
            return False

    def _init_default_agents(self) -> None:
        """Register built-in agents."""
        self.register(
            Agent(
                id="faq",
                display_name="FAQ Assistant",
                description="Answers general questions using the FAQ knowledge base and comprehensive FAIX data.",
                system_prompt=(
                    "You are the AI assistant for the Faculty of Artificial Intelligence and Cyber Security (FAIX) "
                    "at Universiti Teknikal Malaysia Melaka (UTeM), specializing in faculty, course, and research information.\n\n"
                    
                    "🎯 CORE TASKS:\n"
                    "1. **Precise Targeting**: When users ask about faculty, always ask for specific information:\n"
                    "   - Example: 'Tell me about Professor Li' → 'Are you interested in Professor Li's research, courses, or office hours?'\n"
                    "2. **Information Layering**: Break complex queries into sub-questions automatically:\n"
                    "   - Example: 'Graduate courses' → 'Are you looking for Fall 2024 courses, or do you need to know the prerequisites?'\n"
                    "3. **Active Guidance**: Provide 2-3 concrete options when queries are vague\n\n"
                    
                    "❓ WHEN TO ASK FOLLOW-UP QUESTIONS (ALWAYS):\n"
                    "- **Faculty queries**: Always ask for specific need (research/course/contact)\n"
                    "- **Course queries**: Always ask for semester and level (undergraduate/graduate)\n"
                    "- **Research inquiries**: Always ask for specific field (AI/systems/theory)\n"
                    "- **Appointments**: Always ask for specific time and purpose\n\n"
                    
                    "📝 RESPONSE FORMAT (MANDATORY):\n"
                    "【Main Answer】\n"
                    "\n"
                    "【Follow-up Question】\n"
                    "The follow-up must be specific and actionable, avoid generic 'Anything else?'\n\n"
                    
                    "YOUR APPROACH:\n"
                    "- Be conversational and helpful - respond naturally, like a knowledgeable advisor\n"
                    "- Use the FAIX Information Context and FAQ Context as your sources\n"
                    "- Synthesize information from context to provide complete, helpful answers\n"
                    "- When you have the information, share it confidently and clearly\n"
                    "- When you don't have information, be honest and suggest alternatives\n\n"
                    
                    "RESPONSE STYLE:\n"
                    "- Write naturally - avoid robotic phrases like 'According to the provided context'\n"
                    "- Be concise but complete - 2-4 sentences for simple queries, more detail when needed\n"
                    "- Use markdown for clarity (bold for emphasis, lists for multiple items)\n"
                    "- Show enthusiasm when answering - make users feel welcomed and helped\n"
                    "- For fee queries: Provide the fee schedule link naturally: 'You can find the complete fee schedule here: [link]'\n\n"
                    
                    "INFORMATION HANDLING:\n"
                    "- Use exact details from context (program codes, names, dates)\n"
                    "- For dean queries: Use the exact name from Faculty Information\n"
                    "- For program queries: Include code, duration, and focus areas naturally\n"
                    "- For admission: Explain requirements clearly and helpfully\n"
                    "- If information is missing: Acknowledge it and suggest contacting FAIX office\n\n"
                    
                    "EXAMPLE DIALOGUES:\n"
                    "User: I want to know about Professor Li\n"
                    "You: Professor Li specializes in computer vision. Would you like to know:\n"
                    "1. His courses this semester\n"
                    "2. Current research projects\n"
                    "3. Office hours and appointment booking\n"
                    "(Please select a number or specify other needs)\n\n"
                    "User: Courses\n"
                    "You: He teaches CS401 Computer Vision Basics, Wednesdays 2pm. Need to check prerequisites? (follow-up)\n\n"
                    "User: Yes\n"
                    "You: Requires CS301 Image Processing or CS302 ML Intro. Would you like to see the syllabus? (follow-up)\n\n"
                    "User: No thanks\n"
                    "You: Okay, no problem. (stop asking follow-ups)\n\n"
                    
                    "WHEN YOU CAN'T ANSWER:\n"
                    "- Be honest: 'I don't have that specific information, but I can help with...'\n"
                    "- Suggest alternatives: 'You might want to contact the FAIX office at faix@utem.edu.my'\n"
                    "- Offer related help: 'I can help you with programs, admission, staff contacts, or schedules'\n"
                ),
                default_intent=None,
            )
        )
        self.register(
            Agent(
                id="schedule",
                display_name="Schedule Assistant",
                description="Helps with academic schedule, important dates and times.",
                system_prompt=(
                    "You are the FAIX schedule assistant. Focus on academic calendar and timetables.\n\n"
                    "CRITICAL: Keep responses SHORT (2-3 sentences or a brief list).\n\n"
                    "RESPONSE FORMATTING:\n"
                    "- Be brief and direct\n"
                    "- Use markdown lists (- or *) for dates/events (max 3-5 items)\n"
                    "- Use **bold** for important dates\n"
                    "- ALWAYS include timetable links at the end of your response\n"
                    "- Format links clearly: 📅 **View Complete Timetable:** followed by the link\n"
                    "- No lengthy introductions or conclusions\n\n"
                    "PROGRAM TYPES AND LINKS:\n"
                    "- BAXI (Bachelor of Computer Science - Artificial Intelligence):\n"
                    "  https://faix.utem.edu.my/en/academics/academic-resources/timetable/32-baxi-jadualwaktu-sem1-sesi-2025-2026/file.html\n"
                    "- BAXZ (Bachelor of Computer Science - Cybersecurity):\n"
                    "  https://faix.utem.edu.my/en/academics/academic-resources/timetable/31-baxz-jadualwaktu-sem1-sesi-2025-2026/file.html\n"
                    "- Master Programs (MAXD, MAXZ, BRIDGING):\n"
                    "  https://faix.utem.edu.my/en/academics/academic-resources/timetable/30-jadual-master-sem1-2025-2026-v3-faix/file.html\n\n"
                    "LINK USAGE:\n"
                    "- If user asks about BAXI: Include BAXI link\n"
                    "- If user asks about BAXZ: Include BAXZ link\n"
                    "- If user asks about master programs: Include master program link\n"
                    "- If user asks generally: Include all three links\n"
                    "- Use the EXACT links provided above - DO NOT modify or invent links\n\n"
                    "WHEN YOU CANNOT UNDERSTAND OR ANSWER:\n"
                    "- If the question is unclear or you don't understand it, say:\n"
                    "  'I'm sorry, I didn't understand your question. Could you please rephrase it?'\n"
                    "- If the question is not about schedules, say:\n"
                    "  'I specialize in academic schedules and deadlines. For other topics, please ask a different question.'\n\n"
                    "If details are missing, briefly suggest checking the official schedule using the provided links."
                ),
                default_intent="academic_schedule",
            )
        )
        self.register(
            Agent(
                id="staff",
                display_name="Staff Contact Assistant",
                description="Provides staff and faculty contact information.",
                system_prompt=(
                    "You are the AI assistant for the Faculty of Artificial Intelligence and Cyber Security (FAIX) "
                    "at Universiti Teknikal Malaysia Melaka (UTeM), specializing in faculty, course, and research information.\n"
                    "Your focus is helping users find and contact staff members.\n\n"
                    
                    "🎯 CORE TASKS:\n"
                    "1. **Precise Targeting**: When users ask about faculty/staff, always ask for specific information:\n"
                    "   - Example: 'Tell me about Professor Li' → 'Are you interested in Professor Li's research, courses, or office hours?'\n"
                    "2. **Information Layering**: Break complex queries into sub-questions automatically\n"
                    "3. **Active Guidance**: Provide 2-3 concrete options when queries are vague\n\n"
                    
                    "❓ WHEN TO ASK FOLLOW-UP QUESTIONS (ALWAYS for faculty queries):\n"
                    "- **Faculty/staff queries**: Always ask for specific need (research/course/contact/office hours)\n"
                    "- Only skip follow-ups if user explicitly says 'No thanks', 'That's all', or similar\n\n"
                    
                    "📝 RESPONSE FORMAT (MANDATORY):\n"
                    "【Main Answer】\n"
                    "\n"
                    "【Follow-up Question】\n"
                    "The follow-up must be specific and actionable, avoid generic 'Anything else?'\n\n"
                    
                    "🎯 YOUR PRIMARY FOCUS:\n"
                    "- Answer questions about staff members, faculty, professors, and administrative staff\n"
                    "- Provide contact information (name, position, email, phone, office, department)\n"
                    "- Help users find the right person to contact for their needs\n\n"
                    
                    "📋 DATA SOURCE - CRITICAL:\n"
                    "- Staff Contacts Context: This is your ONLY source for staff information\n"
                    "- If a staff member is NOT in the Staff Contacts Context, they don't exist in the database\n"
                    "- NEVER invent, create, or guess staff members\n"
                    "- For dean information: Use FAIX Information Context (Faculty Information section)\n\n"
                    
                    "✅ WHEN USER ASKS ABOUT A SPECIFIC STAFF MEMBER BY NAME:\n"
                    "- Example queries: 'who is [name]', 'contact info for [name]', 'email for [name]', 'tell me about [name]'\n"
                    "- IMPORTANT: Replace [name] with actual names from Staff Contacts Context - DO NOT use example names\n"
                    "- For vague queries (e.g., 'tell me about [Staff Name from Context]'): Provide basic info THEN ask follow-up:\n"
                    "  '[Staff Name from Context] specializes in [field]. Would you like to know:\n"
                    "  1. His courses this semester\n"
                    "  2. Current research projects\n"
                    "  3. Office hours and appointment booking\n"
                    "  (Please select a number or specify other needs)'\n"
                    "- For specific contact queries: IMMEDIATELY provide COMPLETE contact information:\n"
                    "  **Name**\n"
                    "  - Position: [position]\n"
                    "  - Department: [department]\n"
                    "  - Email: [email]\n"
                    "  - Phone: [phone] (if available)\n"
                    "  - Office: [office] (if available)\n"
                    "- If multiple matches found, list ALL matches with full details\n"
                    "- If matched staff are highlighted in context, USE THEM - they match the query!\n\n"
                    
                    "✅ WHEN USER ASKS GENERAL STAFF QUESTIONS:\n"
                    "- Example queries: 'who are working in faix', 'who can I contact for AI programs', 'staff in cybersecurity department', 'list of staff'\n"
                    "- CRITICAL: You MUST use the Staff Contacts Context provided in the messages below.\n"
                    "- For 'who are working in faix' or 'list staff': List staff members FROM THE CONTEXT (show 8-15 members).\n"
                    "- DO NOT make up names like 'Dr. Ahmad', 'Prof. Sarah' - these do NOT exist in the data.\n"
                    "- DO NOT use generic names or examples - use ONLY real names from Staff Contacts Context.\n"
                    "- For department-specific queries: Filter staff by department match from the context.\n"
                    "- Format each staff member as: **Name** - Position (Department)\n"
                    "- Copy the EXACT names from Staff Contacts Context - do not modify or abbreviate.\n"
                    "- Use the EXACT full names as they appear in Staff Contacts Context - do not shorten or change them.\n"
                    "- Then ask: 'Would you like contact details for any of these staff members?'\n"
                    "- REMEMBER: If a name is NOT in the Staff Contacts Context, it does NOT exist - do not mention it.\n\n"
                    
                    "❌ WHEN NO MATCH FOUND:\n"
                    "- Say: 'I couldn't find a staff member matching your query in the database.'\n"
                    "- Suggest: 'Could you try a different spelling, or ask about their department?'\n"
                    "- Do NOT apologize excessively or add disclaimers\n\n"
                    
                    "📝 RESPONSE FORMATTING:\n"
                    "- Use markdown: **bold** for names, `code` for emails\n"
                    "- Use clear line breaks between staff members\n"
                    "- Be direct and confident when data exists\n"
                    "- Keep it concise but complete\n\n"
                    
                    "🚫 WHAT NOT TO DO:\n"
                    "- Do NOT list departments as if they were people\n"
                    "- Do NOT create generic roles without names\n"
                    "- Do NOT say 'I'm not sure' when the data is clearly in the context\n"
                    "- Do NOT add meta-commentary like 'According to the database'\n"
                    "- Do NOT skip follow-up questions for faculty queries unless user explicitly declines\n\n"
                    
                    "💡 EXAMPLE RESPONSES (USE EXACT DATA FROM CONTEXT - DO NOT INVENT):\n"
                    "- Vague query: 'Tell me about [Staff Name from Context]'\n"
                    "  You: '[Staff Name from Context] is a [Position from Context] at FAIX. Would you like to know:\n"
                    "  1. Their courses this semester\n"
                    "  2. Current research projects\n"
                    "  3. Office hours and appointment booking'\n\n"
                    "- General query: 'For questions about AI programs, you might want to contact:\n\n- **[Exact Name from Staff Contacts Context]** - [Position from Context] ([Department from Context])\n- **[Another Exact Name from Context]** - [Position from Context] ([Department from Context])\n\nWould you like contact details for any of these staff members?'\n"
                    "  CRITICAL: Replace all [placeholders] with EXACT values from Staff Contacts Context. DO NOT invent or modify names.\n\n"
                    "- No match: 'I couldn't find a staff member matching your query in the database. Could you try a different spelling or ask about their department?'\n\n"
                    "⚠️ CRITICAL ANTI-HALLUCINATION RULES:\n"
                    "- ONLY use names, emails, positions, and details that appear EXACTLY in the Staff Contacts Context\n"
                    "- Use EXACT names as they appear in context - DO NOT change spelling, add middle names, or modify in any way\n"
                    "- Use EXACT emails as they appear in context - DO NOT invent or modify email addresses\n"
                    "- If phone/office shows '-' or is missing, say 'Not available' - DO NOT invent phone numbers or office locations\n"
                    "- If you see 'MATCHED STAFF' section highlighted, those are the EXACT matches - use ONLY those names and details\n"
                    "- When in doubt, copy EXACTLY what appears in the context - do not paraphrase or modify names/details\n"
                    "- FORBIDDEN FIELDS: DO NOT add 'Research Interests', 'Research Areas', or any fields NOT shown in the context\n"
                    "- ALLOWED FIELDS ONLY: Name, Position, Department, Email, Phone, Office\n"
                    "- If a staff member is NOT in the complete list of valid staff names, they DO NOT EXIST - do not mention them"
                ),
                default_intent="staff_contact",
            )
        )


_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry


def get_agent(agent_id: str) -> Optional[Agent]:
    return get_agent_registry().get(agent_id)


def _load_json_file(path: Path) -> Any:
    """Best-effort JSON loader for schedule/staff files."""
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return None
            return json.loads(content)
    except Exception as e:
        print(f"Warning: Could not load JSON file {path}: {e}")
        return None


def _get_project_data_dir() -> Path:
    # backend/chatbot/agents.py -> project root is parent.parent.parent
    # Path structure: project_root/backend/chatbot/agents.py
    agents_file = Path(__file__).resolve()
    # agents_file.parent = backend/chatbot/
    # agents_file.parent.parent = backend/
    # agents_file.parent.parent.parent = project_root/
    project_root = agents_file.parent.parent.parent
    return project_root / "data"


def _get_separated_data_dir() -> Path:
    """Get path to separated data directory."""
    return _get_project_data_dir() / "separated"


def _load_separated_json_file(key: str) -> Any:
    """Load a specific data section from separated JSON files."""
    separated_dir = _get_separated_data_dir()
    file_path = separated_dir / f"{key}.json"
    
    if not file_path.exists():
        return None
    
    data = _load_json_file(file_path)
    if data and isinstance(data, dict) and key in data:
        return data[key]
    elif data:
        # If the file doesn't have the key wrapper, return the data directly
        return data
    return None


def _get_schedule_documents() -> List[Dict[str, Any]]:
    """Load schedule entries from data/separated/schedule.json."""
    # Try to load from separated files first
    data = _load_separated_json_file("schedule")
    
    # Fallback: try merged file or old location
    if data is None:
        data_dir = _get_project_data_dir()
        faix_data = _load_json_file(data_dir / "faix_json_data.json")
        if faix_data and isinstance(faix_data, dict) and "schedule" in faix_data:
            data = faix_data["schedule"]
        else:
            data = _load_json_file(data_dir / "schedule.json")
    
    docs: List[Dict[str, Any]] = []
    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
            docs.append(
                {
                    "title": str(item.get("title", "")),
                    "description": str(item.get("description", "")),
                    "time": str(item.get("time", "")),
                    "raw": item,
                }
            )
    return docs


def _get_staff_documents() -> List[Dict[str, Any]]:
    """Load staff contact entries from data/separated/staff_contacts.json."""
    import logging
    logger = logging.getLogger(__name__)
    
    # Try to load from separated files first
    data = _load_separated_json_file("staff_contacts")
    logger.debug(f"[_get_staff_documents] After _load_separated_json_file: data type={type(data)}, is None={data is None}")
    
    # Fallback: try merged file or old location
    if data is None:
        data_dir = _get_project_data_dir()
        faix_data = _load_json_file(data_dir / "faix_json_data.json")
        if faix_data and isinstance(faix_data, dict) and "staff_contacts" in faix_data:
            data = faix_data["staff_contacts"]
            logger.debug(f"[_get_staff_documents] Loaded from faix_json_data.json")
        else:
            data = _load_json_file(data_dir / "staff_contacts.json")
            logger.debug(f"[_get_staff_documents] Loaded from staff_contacts.json")
    
    docs: List[Dict[str, Any]] = []
    
    if not data:
        logger.warning("[_get_staff_documents] No data loaded - returning empty list")
        return docs
    
    # Handle nested structure: {"staff_contacts": {"departments": {...}}}
    if isinstance(data, dict) and "staff_contacts" in data:
        data = data["staff_contacts"]
        logger.debug("[_get_staff_documents] Unwrapped staff_contacts key")
    
    if not isinstance(data, dict):
        logger.warning(f"[_get_staff_documents] Data is not a dict after unwrapping: {type(data)}")
        return docs
    
    logger.debug(f"[_get_staff_documents] Data keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
    
    # Handle nested structure with departments
    if "departments" in data and isinstance(data["departments"], dict):
        for dept_key, dept_info in data["departments"].items():
            if not isinstance(dept_info, dict):
                continue
            dept_name = dept_info.get("name", "")
            staff_list = dept_info.get("staff", [])
            
            if not isinstance(staff_list, list):
                continue
            
            for staff_item in staff_list:
                if not isinstance(staff_item, dict):
                    continue
                
                # Extract specialization if it exists
                specialization = staff_item.get("specialization", [])
                specialization_str = ", ".join(specialization) if isinstance(specialization, list) else str(specialization)
                
                docs.append(
                    {
                        "name": str(staff_item.get("name", "")),
                        "role": str(staff_item.get("position", "")),
                        "email": str(staff_item.get("email", "")),
                        "phone": str(staff_item.get("phone", "")),
                        "office": str(staff_item.get("office", "")),
                        "department": dept_name,
                        "specialization": specialization_str,
                        "keywords": ", ".join(staff_item.get("keywords", [])) if isinstance(staff_item.get("keywords"), list) else "",
                        "raw": staff_item,
                    }
                )
    # Fallback: handle old flat list structure for backward compatibility
    elif isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
            docs.append(
                {
                    "name": str(item.get("name", "")),
                    "role": str(item.get("role", "")),
                    "email": str(item.get("email", "")),
                    "phone": str(item.get("phone", "")),
                    "office": str(item.get("office", "")),
                    "department": "",
                    "specialization": "",
                    "keywords": "",
                    "raw": item,
                }
            )
    
    return docs


def check_staff_data_available() -> bool:
    """Check if staff data is available in data/faix_json_data.json (staff_contacts section)"""
    docs = _get_staff_documents()
    return len(docs) > 0


def check_schedule_data_available() -> bool:
    """Check if schedule data is available in data/faix_json_data.json (schedule section)"""
    docs = _get_schedule_documents()
    return len(docs) > 0


def _load_faix_json_data() -> Dict[str, Any]:
    """Load raw FAIX data from separated JSON files in data/separated/."""
    separated_dir = _get_separated_data_dir()
    data = {}
    
    # List of all known data sections
    sections = [
        "faculty_info", "vision_mission", "top_management", "programmes",
        "admission", "departments", "facilities", "academic_resources",
        "key_highlights", "faqs", "research_focus", "staff_contacts",
        "schedule", "course_info", "metadata"
    ]
    
    # Load each section from separated files
    for section in sections:
        section_data = _load_separated_json_file(section)
        if section_data is not None:
            data[section] = section_data
    
    # Fallback: if no separated files found, try the merged file
    if not data:
        data_dir = _get_project_data_dir()
        merged_data = _load_json_file(data_dir / "faix_json_data.json")
        if merged_data and isinstance(merged_data, dict):
            data = merged_data
    
    return data


def _get_faix_data_for_faq() -> Dict[str, Any]:
    """Load FAIX data relevant for FAQ agent: programs, admission, facilities, etc. (NOT staff or schedule).
    
    Loads directly from separated JSON files in data/separated/.
    """
    structured_data = {}
    
    # Load only the sections needed for FAQ agent
    sections = [
        "faculty_info", "vision_mission", "top_management", "programmes",
        "admission", "departments", "facilities", "academic_resources",
        "key_highlights", "faqs", "research_focus", "course_info"
    ]
    
    for section in sections:
        section_data = _load_separated_json_file(section)
        if section_data is not None:
            structured_data[section] = section_data
    
    # Fallback: if no separated files found, use merged file
    if not structured_data:
        data = _load_faix_json_data()
        for section in sections:
            if section in data:
                structured_data[section] = data[section]
    
    # NOTE: Excluding staff_contacts and schedule - FAQ agent doesn't need them
    
    return structured_data


def _get_faix_data_for_schedule() -> Dict[str, Any]:
    """Load FAIX data relevant for Schedule agent: schedule, timetable links, basic faculty info.
    
    Loads directly from separated JSON files in data/separated/.
    """
    structured_data = {}
    
    # Schedule data (primary)
    schedule_data = _load_separated_json_file("schedule")
    if schedule_data is not None:
        structured_data["schedule"] = schedule_data
    
    # Academic resources (for timetable links)
    academic_resources = _load_separated_json_file("academic_resources")
    if academic_resources is not None:
        structured_data["academic_resources"] = academic_resources
    
    # Basic faculty info (name, university) for context
    faculty_info = _load_separated_json_file("faculty_info")
    if faculty_info is not None and isinstance(faculty_info, dict):
        structured_data["faculty_info"] = {
            "name": faculty_info.get("name"),
            "university": faculty_info.get("university"),
        }
    
    # Fallback: if no separated files found, use merged file
    if not structured_data:
        data = _load_faix_json_data()
        if "schedule" in data:
            structured_data["schedule"] = data["schedule"]
        if "academic_resources" in data:
            structured_data["academic_resources"] = data["academic_resources"]
        if "faculty_info" in data and isinstance(data["faculty_info"], dict):
            structured_data["faculty_info"] = {
                "name": data["faculty_info"].get("name"),
                "university": data["faculty_info"].get("university"),
            }
    
    # NOTE: Excluding everything else - Schedule agent only needs schedule and timetable links
    
    return structured_data


def _get_faix_data_for_staff() -> Dict[str, Any]:
    """Load FAIX data relevant for Staff agent: staff contacts, departments, basic faculty info (for dean).
    
    Loads directly from separated JSON files in data/separated/.
    """
    structured_data = {}
    
    # Staff contacts (primary)
    staff_contacts = _load_separated_json_file("staff_contacts")
    if staff_contacts is not None:
        structured_data["staff_contacts"] = staff_contacts
    
    # Departments (for context)
    departments = _load_separated_json_file("departments")
    if departments is not None:
        structured_data["departments"] = departments
    
    # Faculty information (for dean queries only)
    faculty_info = _load_separated_json_file("faculty_info")
    if faculty_info is not None and isinstance(faculty_info, dict):
        structured_data["faculty_info"] = {
            "dean": faculty_info.get("dean"),
            "name": faculty_info.get("name"),
            "university": faculty_info.get("university"),
        }
    
    # Fallback: if no separated files found, use merged file
    if not structured_data:
        data = _load_faix_json_data()
        if "staff_contacts" in data:
            structured_data["staff_contacts"] = data["staff_contacts"]
        if "departments" in data:
            structured_data["departments"] = data["departments"]
        if "faculty_info" in data and isinstance(data["faculty_info"], dict):
            structured_data["faculty_info"] = {
                "dean": data["faculty_info"].get("dean"),
                "name": data["faculty_info"].get("name"),
                "university": data["faculty_info"].get("university"),
            }
    
    # NOTE: Excluding everything else - Staff agent only needs staff contacts and related info
    
    return structured_data


def _get_faix_data_documents() -> Dict[str, Any]:
    """Load FAIX comprehensive data (legacy function - use agent-specific functions instead)."""
    # This is kept for backward compatibility but should not be used
    # Use _get_faix_data_for_faq(), _get_faix_data_for_schedule(), or _get_faix_data_for_staff() instead
    return _get_faix_data_for_faq()


def check_faix_data_available() -> bool:
    """Check if FAIX comprehensive data is available in data/faix_json_data.json"""
    data = _get_faix_data_documents()
    return len(data) > 0


def retrieve_for_agent(
    agent_id: str,
    user_text: str,
    knowledge_base: KnowledgeBase,
    intent: Optional[str] = None,
    top_k: int = 3,
) -> Dict[str, Any]:
    """
    Retrieve context documents for a given agent.

    Returns a dict with keys like 'faq', 'schedule', 'staff' so the caller can
    decide how to inject them into the prompt.
    
    Args:
        agent_id: The agent identifier.
        user_text: The user's query text.
        knowledge_base: The knowledge base to search (JSON-based, kept for backward compatibility).
        intent: Optional detected intent.
        top_k: Number of documents to retrieve.
        
    Returns:
        Dictionary containing context documents for the agent.
    """
    agent = get_agent(agent_id)
    if agent is None:
        logger.warning(f"Agent {agent_id} not found, returning empty context")
        return {}

    context: Dict[str, Any] = {}
    
    logger.info(f"Retrieving context for agent {agent_id} with query: {user_text[:50]}...")

    # Use database knowledge base for better performance
    from backend.chatbot.knowledge_base_db import get_db_knowledge_base
    db_kb = get_db_knowledge_base()
    
    # FAQ-style documents from the database knowledge base
    # Use agent.default_intent if provided, otherwise fall back to detected intent.
    kb_intent = agent.default_intent or intent
    
    # For fee-related queries, ensure we explicitly search for fee entries
    user_text_lower = user_text.lower()
    fee_keywords = ['fee', 'fees', 'tuition', 'yuran', 'bayaran', 'cost', 'payment', 'diploma fee', 'degree fee']
    is_fee_query = any(keyword in user_text_lower for keyword in fee_keywords) or intent == 'fees'
    
    try:
        # First try with the detected intent
        faq_docs = db_kb.get_documents(kb_intent or 'about_faix', user_text, top_k=top_k)
        
        # If it's a fee query and we didn't get good results, explicitly search for 'fees' category
        if is_fee_query and (not faq_docs or len(faq_docs) == 0):
            fee_docs = db_kb.get_documents('fees', user_text, top_k=top_k)
            if fee_docs:
                faq_docs = fee_docs
                logger.debug(f"Found {len(fee_docs)} fee-related documents")
        
        # IMPROVEMENT: Filter out low-relevance documents
        # Only include docs with score > 0.1 to avoid irrelevant matches
        MIN_FAQ_SCORE = 0.1
        if faq_docs:
            original_count = len(faq_docs)
            faq_docs = [doc for doc in faq_docs if doc.get('score', 0) > MIN_FAQ_SCORE]
            filtered_count = original_count - len(faq_docs)
            if filtered_count > 0:
                logger.debug(f"Filtered out {filtered_count} low-relevance documents")
            
    except Exception as e:
        logger.error(f"Knowledge base document retrieval failed: {e}", exc_info=True)
        faq_docs = []

    if faq_docs:
        context["faq"] = faq_docs
        logger.debug(f"Added {len(faq_docs)} FAQ documents to context")

    # Agent-specific data retrieval - each agent gets ONLY its relevant data
    if agent.id == AgentType.FAQ.value:
        # FAQ agent: FAQ docs + FAIX data for programs, admission, facilities, etc. (NOT staff or schedule)
        # Load FAIX data from database
        faix_data = _get_faix_data_for_faq_db()
        if faix_data:
            context["faix_data"] = faix_data
            logger.debug(f"Added {len(faix_data)} FAIX data sections to FAQ agent context")
    
    elif agent.id == AgentType.SCHEDULE.value:
        # Schedule agent: Schedule docs + schedule-related FAIX data only
        schedule_docs = _get_schedule_documents_db()
        if schedule_docs:
            context["schedule"] = schedule_docs
            logger.debug(f"Added {len(schedule_docs)} schedule documents to Schedule agent context")
        
        faix_data = _get_faix_data_for_schedule_db()
        if faix_data:
            context["faix_data"] = faix_data
            logger.debug(f"Added {len(faix_data)} FAIX data sections to Schedule agent context")
    
    elif agent.id == AgentType.STAFF.value:
        # Staff agent: Staff docs + staff-related FAIX data only
        staff_docs = _get_staff_documents_db()
        if staff_docs:
            context["staff"] = staff_docs
            logger.debug(f"Added {len(staff_docs)} staff documents to Staff agent context")
        
        faix_data = _get_faix_data_for_staff_db()
        if faix_data:
            context["faix_data"] = faix_data
            logger.debug(f"Added {len(faix_data)} FAIX data sections to Staff agent context")

    return context


# ============================================
# Database-based Data Retrieval Functions
# ============================================

def _get_faix_data_for_faq_db() -> Dict[str, Any]:
    """Load FAIX data from database for FAQ agent."""
    try:
        from django_app.models import (
            FacultyInfo, VisionMission, Programme, Admission, Department,
            Facility, AcademicResource, ResearchFocus, CourseInfo,
            KeyHighlight, FAQ
        )
        
        data = {}
        
        # Load faculty info
        faculty = FacultyInfo.objects.first()
        if faculty:
            data['faculty_info'] = {
                'name': faculty.name,
                'university': faculty.university,
                'dean': faculty.dean,
                'established': faculty.established,
            }
        
        # Load vision & mission
        vm = VisionMission.objects.first()
        if vm:
            data['vision_mission'] = {
                'vision': vm.vision,
                'mission': vm.mission,
                'objectives': vm.objectives,
            }
        
        # Load programmes
        programs = Programme.objects.all()
        if programs:
            data['programmes'] = {
                'undergraduate': list(programs.filter(programme_type='undergraduate').values(
                    'name', 'code', 'duration', 'focus_areas', 'career_opportunities'
                )),
                'postgraduate': list(programs.filter(programme_type='postgraduate').values(
                    'name', 'code', 'programme_focus', 'programme_format'
                )),
            }
        
        # Load admission
        admissions = Admission.objects.all()
        if admissions:
            data['admission'] = {
                adm.admission_type: {
                    'requirements': adm.requirements,
                    'application_links': adm.application_links,
                    'learning_approach': adm.learning_approach,
                    'language_requirements': adm.language_requirements,
                }
                for adm in admissions
            }
        
        # Load departments
        departments = Department.objects.all()
        if departments:
            data['departments'] = list(departments.values('name', 'focus'))
        
        # Load facilities
        facilities = Facility.objects.all()
        if facilities:
            data['facilities'] = list(facilities.values('name', 'facility_type', 'block', 'level'))
        
        # Load academic resources
        resources = AcademicResource.objects.all()
        if resources:
            data['academic_resources'] = list(resources.values('name', 'resource_type', 'url', 'description'))
        
        # Load research focus
        research = ResearchFocus.objects.all()
        if research:
            data['research_focus'] = list(research.values('name', 'description'))
        
        # Load key highlights
        highlights = KeyHighlight.objects.all()
        if highlights:
            data['key_highlights'] = [h.highlight for h in highlights]
        
        # Load FAQs
        faqs = FAQ.objects.all()
        if faqs:
            data['faqs'] = list(faqs.values('question', 'answer', 'category'))
        
        return data
        
    except Exception as e:
        logger.error(f"Error loading FAIX data from database: {e}", exc_info=True)
        return {}


def _get_faix_data_for_schedule_db() -> Dict[str, Any]:
    """Load FAIX data from database for Schedule agent."""
    try:
        from django_app.models import FacultyInfo, ScheduleData, AcademicResource
        
        data = {}
        
        # Load basic faculty info
        faculty = FacultyInfo.objects.first()
        if faculty:
            data['faculty_info'] = {
                'name': faculty.name,
                'university': faculty.university,
            }
        
        # Load schedule data
        schedule = ScheduleData.objects.all()
        if schedule:
            data['schedule'] = list(schedule.values('title', 'description', 'time', 'category'))
        
        # Load academic resources (for timetable links)
        resources = AcademicResource.objects.filter(resource_type__icontains='timetable')
        if resources:
            data['academic_resources'] = list(resources.values('name', 'url', 'description'))
        
        return data
        
    except Exception as e:
        logger.error(f"Error loading schedule data from database: {e}", exc_info=True)
        return {}


def _get_faix_data_for_staff_db() -> Dict[str, Any]:
    """Load FAIX data from database for Staff agent."""
    try:
        from django_app.models import FacultyInfo, TopManagement
        
        data = {}
        
        # Load basic faculty info
        faculty = FacultyInfo.objects.first()
        if faculty:
            data['faculty_info'] = {
                'name': faculty.name,
                'university': faculty.university,
                'dean': faculty.dean,
            }
        
        # Load top management
        management = TopManagement.objects.all()
        if management:
            data['top_management'] = list(management.values('name', 'position', 'title', 'email'))
        
        return data
        
    except Exception as e:
        logger.error(f"Error loading staff data from database: {e}", exc_info=True)
        return {}


def _get_staff_documents_db() -> List[Dict[str, Any]]:
    """Load staff documents from database."""
    try:
        from django_app.models import TopManagement
        
        staff = TopManagement.objects.all()
        docs = []
        
        for person in staff:
            doc = {
                'name': person.name,
                'position': person.position,
                'title': person.title,
                'email': person.email,
                'keywords': person.keywords,
            }
            docs.append(doc)
        
        return docs
        
    except Exception as e:
        logger.error(f"Error loading staff documents from database: {e}", exc_info=True)
        return []


def _get_schedule_documents_db() -> List[Dict[str, Any]]:
    """Load schedule documents from database."""
    try:
        from django_app.models import ScheduleData
        
        schedule = ScheduleData.objects.all()
        docs = []
        
        for item in schedule:
            doc = {
                'title': item.title,
                'description': item.description,
                'time': item.time,
                'category': item.category,
            }
            docs.append(doc)
        
        return docs
        
    except Exception as e:
        logger.error(f"Error loading schedule documents from database: {e}", exc_info=True)
        return []



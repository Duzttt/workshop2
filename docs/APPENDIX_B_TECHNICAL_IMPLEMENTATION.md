# Appendix B: Technical Implementation & Code Snippets

This appendix provides the raw technical implementation details for the core logic components described in Chapter 4. These snippets are taken directly from the production codebase.

## 1. Query Processing Logic (Regex)
**File:** `backend/nlp/query_preprocessing.py`

The system uses specific Regular Expressions (RegEx) to extract structured entities before they reach the LLM. This ensures high precision for critical data like emails and course codes.

### 1.1 Email Extraction
Captures standard email formats to identify staff contact queries or user inputs.
```python
# Standard email pattern
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
```

### 1.2 Course Code Extraction
Captures FAIX-specific program codes (BAXI, BAXZ, BITZ, BAXS) with optional year codes.
```python
# Matches program codes like BAXI, BAXZ
program_code_pattern = r'\b(BAXI|BAXZ|BITZ|BAXS)\b'

# Matches specific course codes with numbers (e.g., BAXI 1234)
course_code_with_num = r'\b(BAXI|BAXZ|BITZ|BAXS)\s?\d{3,4}\b'
```

---

## 2. Intent Configuration
**File:** `data/intent_config.json`

This configuration file maps user intent categories to specific keywords and data sections. It serves as the "brain" for the rule-based router.

```json
{
  "intent_categories": [
    "program_info",
    "admission",
    "fees",
    "staff_contact",
    "academic_schedule"
  ],
  "intent_descriptions": {
    "program_info": "Questions about FAIX programmes - BAXI, BAXZ, Master degrees...",
    "staff_contact": "Questions about contacting staff members, faculty, professors...",
    "fees": "Questions about tuition fees, payment schedules, fee structure..."
  },
  "keyword_patterns": {
    "program_info": [
      "program", "degree", "bachelor", "master", "BAXI", "BAXZ", 
      "AI programme", "cybersecurity programme", "computer science"
    ],
    "staff_contact": [
      "contact", "email", "phone", "professor", "lecturer", 
      "who can i contact", "coordinator", "admin"
    ],
    "fees": [
      "fee", "fees", "tuition", "yuran", "cost", "price", "scholarship"
    ]
  },
  "faix_data_mapping": {
    "program_info": ["programmes", "programmes.undergraduate"],
    "staff_contact": ["staff_contacts", "departments"],
    "fees": ["admission.undergraduate_local.application_links.fees"]
  }
}
```

---

## 3. Prompt Engineering
**File:** `backend/chatbot/agents.py`

The system uses specialized system prompts to ground the LLM in the retrieved context and prevent hallucinations. Below is the prompt for the **FAQ Assistant**.

```python
system_prompt=(
    "You are the AI assistant for the Faculty of Artificial Intelligence and Cyber Security (FAIX) "
    "at Universiti Teknikal Malaysia Melaka (UTeM), specializing in faculty, course, and research information.\n\n"
    
    "🎯 CORE TASKS:\n"
    "1. **Precise Targeting**: When users ask about faculty, always ask for specific information:\n"
    "   - Example: 'Tell me about Professor Li' → 'Are you interested in Professor Li's research, courses, or office hours?'\n"
    "2. **Information Layering**: Break complex queries into sub-questions automatically:\n"
    "   - Example: 'Graduate courses' → 'Are you looking for Fall 2024 courses, or do you need to know the prerequisites?'\n"
    "3. **Active Guidance**: Provide 2-3 concrete options when queries are vague\n\n"
    
    "📝 RESPONSE FORMAT (MANDATORY):\n"
    "【Main Answer】\n"
    "\n"
    "【Follow-up Question】\n"
    "The follow-up must be specific and actionable, avoid generic 'Anything else?'\n\n"
    
    "YOUR APPROACH:\n"
    "- Be conversational and helpful - respond naturally, like a knowledgeable advisor\n"
    "- Use the FAIX Information Context and FAQ Context as your sources\n"
    "- Synthesize information from context to provide complete, helpful answers\n"
    "- When you don't have information, be honest and suggest alternatives\n\n"
    
    "INFORMATION HANDLING:\n"
    "- Use exact details from context (program codes, names, dates)\n"
    "- For dean queries: Use the exact name from Faculty Information\n"
    "- For program queries: Include code, duration, and focus areas naturally\n"
    "- If information is missing: Acknowledge it and suggest contacting FAIX office\n\n"
)
```

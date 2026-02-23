# Appendix C: Knowledge Base Samples

This appendix demonstrates the quality and structure of the data the chatbot uses to provide accurate, grounded answers. The data is stored in structured JSON files to enable both direct retrieval (by agents) and semantic search (via embeddings).

## 1. Structured Data (FAIX Faculty Information)
**File:** `data/faix_json_data.json`

This file serves as the "Ground Truth" for the RAG system. It contains hierarchical data covering faculty details, programs, and staff.

### 1.1 Faculty Vision & Mission
```json
"faculty_info": {
  "name": "Faculty of Artificial Intelligence and Cyber Security (FAIX)",
  "university": "Universiti Teknikal Malaysia Melaka (UTeM)",
  "established": "July 22, 2024",
  "dean": "Associate Professor Ts. Dr. Muhammad Hafidz Fazli Bin Md Fauadi",
  "contact": {
    "email": "faix@utem.edu.my",
    "phone": "+606 270 4540",
    "website": "https://faix.utem.edu.my/en/"
  }
},
"vision_mission": {
  "vision": "To be a leading faculty in producing skilled AI and cybersecurity professionals to meet Malaysia's goal of cultivating 200,000 AI specialists and 100,000 cyber security experts by 2030",
  "mission": "To advance education, research, and development of high-caliber professionals in AI and cyber security disciplines through innovation, industry collaboration, and future-ready curriculum"
}
```

### 1.2 Programme Details (BAXI - Artificial Intelligence)
```json
"programmes": {
  "undergraduate": [
    {
      "name": "Bachelor of Computer Science (Artificial Intelligence) with Honours",
      "code": "BAXI",
      "duration": "4 years",
      "focus_areas": [
        "AI technology",
        "Machine learning",
        "Neural networks",
        "Fuzzy logic",
        "Evolutionary computing",
        "Intelligent agents"
      ],
      "career_opportunities": [
        "Knowledge engineer",
        "Smart systems developer",
        "Expert system developer",
        "Systems analyst"
      ],
      "learning_distribution": {
        "coursework": "70%",
        "practical_projects": "30%"
      }
    }
  ]
}
```

### 1.3 Staff Directory (Sample)
```json
"staff_contacts": {
  "departments": {
    "administration": {
      "name": "Administration",
      "staff": [
        {
          "name": "Mdm. Nur Azriah Binti Amir",
          "position": "Deputy Registrar",
          "email": "azriah@utem.edu.my",
          "keywords": ["registrar", "admin", "azriah"]
        }
      ]
    },
    "academic": {
      "name": "Academic Staff",
      "staff": [
        {
          "name": "Professor Ts. Dr. Burhanuddin Bin Mohd Aboobaider",
          "position": "Professor",
          "email": "burhanuddin@utem.edu.my",
          "keywords": ["aboobaider", "professor", "burhanuddin"]
        }
      ]
    }
  }
}
```

---

## 2. FAQ Dataset
**File:** `data/separated/faqs.json`

This dataset contains verified Question-Answer pairs used for semantic similarity matching.

```json
{
  "faqs": [
    {
      "question": "What programmes does FAIX offer?",
      "answer": "FAIX offers 2 undergraduate programmes (AI and Computer Security) and 3 postgraduate programmes (Security Science, Data Science and Analytics including ODL option).",
      "category": "programmes"
    },
    {
      "question": "When was FAIX established?",
      "answer": "FAIX was officially founded on July 22, 2024.",
      "category": "about"
    },
    {
      "question": "What are the postgraduate entry requirements?",
      "answer": "Requirements vary based on background: Computing graduates need minimum CGPA 2.50, non-computing graduates may need prerequisite courses. MUET Band 4 or CEFR Low B2 required.",
      "category": "admission"
    },
    {
      "question": "How can I contact FAIX?",
      "answer": "Email: faix@utem.edu.my, Phone: +606 270 4540, Website: https://faix.utem.edu.my/en/",
      "category": "contact"
    },
    {
      "question": "What is the learning approach at FAIX?",
      "answer": "FAIX emphasizes practical learning with 70% coursework and 30% hands-on, real-world projects to ensure industry readiness.",
      "category": "academics"
    }
  ]
}
```

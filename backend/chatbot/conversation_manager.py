"""
Conversation Management Module for AI Chatbot Assistance for Students (FAIX).

This module handles conversation context, topic tracking, and user intent detection
using a rule-based approach. It manages conversation flow and provides appropriate
responses based on detected topics and fallback mechanisms.

Features:
- Conversation context and history management
- Topic detection (registration, contact, farewell)
- Fallback responses for unclear inputs
- Follow-up question handling within the same context
- Integration-ready for NLP and Knowledge Base modules
- Enhanced error handling and logging
"""

import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Configure logger
logger = logging.getLogger(__name__)


class Intent(Enum):
    """Enum for supported conversation intents."""
    REGISTRATION = "registration"
    CONTACT = "contact"
    FAREWELL = "farewell"
    GREETING = "greeting"
    UNCLEAR = "unclear"


@dataclass
class ConversationContext:
    """Data class to hold conversation context."""
    history: list = field(default_factory=list)
    current_topic: Optional[str] = None
    last_question: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialization."""
        return {
            "history": self.history,
            "current_topic": self.current_topic,
            "last_question": self.last_question,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """Create context from dictionary."""
        return cls(
            history=data.get("history", []),
            current_topic=data.get("current_topic"),
            last_question=data.get("last_question"),
            metadata=data.get("metadata", {}),
        )


class IntentDetector:
    """
    Detects user intent from message content using keyword matching.
    
    This is a simple rule-based approach. In the future, this can be replaced
    with an NLP module (e.g., intent classification from transformer models).
    """
    
    # Keywords for different intents
    KEYWORDS = {
        Intent.REGISTRATION: ["register", "registration", "course", "subject", "enroll", "enrollment"],
        Intent.CONTACT: ["contact", "office", "email", "phone", "staff", "reach", "address"],
        Intent.FAREWELL: ["thanks", "thank", "bye", "goodbye", "see you", "quit", "exit"],
        Intent.GREETING: ["hi", "hello", "hey", "greetings", "help"],
    }
    
    @classmethod
    def detect(cls, user_message: str) -> Optional[Intent]:
        """
        Detects user intent from the message content.
        
        Args:
            user_message: The user's input text.
            
        Returns:
            The detected Intent enum, or None if no clear intent is found.
        """
        if not user_message or not user_message.strip():
            logger.debug("Empty message received for intent detection")
            return None
        
        user_message_lower = user_message.lower().strip()
        
        # Check each intent category
        for intent, keywords in cls.KEYWORDS.items():
            if any(keyword in user_message_lower for keyword in keywords):
                logger.debug(f"Detected intent: {intent.value} from message: {user_message[:50]}...")
                return intent
        
        logger.debug(f"No clear intent detected for message: {user_message[:50]}...")
        return None


def detect_intent(user_message: str) -> Optional[str]:
    """
    Detects user intent from the message content using keyword matching.
    
    This is a simple rule-based approach. In the future, this can be replaced
    with an NLP module (e.g., intent classification from transformer models).
    
    Args:
        user_message: The user's input text.
        
    Returns:
        The detected topic/intent as a string, or None if no clear intent is found.
    """
    intent = IntentDetector.detect(user_message)
    return intent.value if intent else None


class RegistrationHandler:
    """Handles registration-related queries with context-aware responses."""
    
    @staticmethod
    def handle(user_message: str, context: ConversationContext) -> str:
        """
        Handles queries related to course registration and enrollment.
        
        Args:
            user_message: The user's input text.
            context: The conversation context.
            
        Returns:
            An appropriate response about registration.
        """
        user_message_lower = user_message.lower()
        
        # Check for specific sub-questions within registration topic
        if any(word in user_message_lower for word in ["when", "date", "time", "deadline"]):
            return (
                "📅 Registration typically opens at the beginning of each semester. "
                "For specific dates, please check the official FAIX schedule at our website "
                "or contact the registrar's office. Is there anything else about registration?"
            )
        elif any(word in user_message_lower for word in ["how", "form", "process", "step"]):
            return (
                "📝 To register for courses, you'll need to:\n"
                "1. Log into your student portal\n"
                "2. Navigate to 'Course Registration'\n"
                "3. Select your desired courses\n"
                "4. Confirm and submit your registration\n\n"
                "For detailed instructions, please contact the registration office. Need help?"
            )
        elif any(word in user_message_lower for word in ["requirement", "prerequisite", "condition"]):
            return (
                "✅ Course requirements vary by program. Please refer to your course catalog "
                "or speak with your academic advisor for prerequisite information."
            )
        else:
            return (
                "💡 I can help you with registration questions. "
                "Would you like to know about registration dates, the registration process, or course requirements?"
            )


def handle_registration_query(user_message: str, context: Dict[str, Any]) -> str:
    """
    Handles queries related to course registration and enrollment.
    
    Args:
        user_message: The user's input text.
        context: The conversation context dictionary.
        
    Returns:
        An appropriate response about registration.
    """
    ctx = ConversationContext.from_dict(context) if isinstance(context, dict) else context
    return RegistrationHandler.handle(user_message, ctx)


class ContactHandler:
    """Handles contact-related queries with context-aware responses."""
    
    @staticmethod
    def handle(user_message: str, context: ConversationContext) -> str:
        """
        Handles queries related to contacting FAIX staff and services.
        
        Args:
            user_message: The user's input text.
            context: The conversation context.
            
        Returns:
            Contact information or appropriate guidance.
        """
        user_message_lower = user_message.lower()
        
        # Check for specific contact-related sub-questions
        if any(word in user_message_lower for word in ["email", "mail"]):
            return (
                "📧 For email inquiries, please contact the FAIX administrative office. "
                "You can find staff email addresses in our directory on the FAIX website."
            )
        elif any(word in user_message_lower for word in ["phone", "call", "number"]):
            return (
                "☎️ For phone inquiries, please call the FAIX main office. "
                "The contact number is available on our website."
            )
        elif any(word in user_message_lower for word in ["office", "location", "address", "visit"]):
            return (
                "🏢 The FAIX offices are located on the UTeM campus. "
                "For specific office locations and visiting hours, please visit the FAIX website."
            )
        else:
            return (
                "📞 I can help you find contact information for FAIX staff. "
                "Would you like email addresses, phone numbers, or office locations?"
            )


def handle_contact_query(user_message: str, context: Dict[str, Any]) -> str:
    """
    Handles queries related to contacting FAIX staff and services.
    
    Args:
        user_message: The user's input text.
        context: The conversation context dictionary.
        
    Returns:
        Contact information or appropriate guidance.
    """
    ctx = ConversationContext.from_dict(context) if isinstance(context, dict) else context
    return ContactHandler.handle(user_message, ctx)


class GreetingHandler:
    """Handles greeting messages."""
    
    @staticmethod
    def handle(user_message: str) -> str:
        """
        Handles greeting messages from the user.
        
        Args:
            user_message: The user's input text.
            
        Returns:
            A friendly greeting response.
        """
        return (
            "👋 Hello! Welcome to FAIX AI Chatbot. I'm here to help you with questions about "
            "course registration, staff contacts, schedules, and other student inquiries. "
            "How can I assist you today?"
        )


class FallbackHandler:
    """Handles unclear or unrecognized queries."""
    
    @staticmethod
    def handle() -> str:
        """
        Provides a polite fallback response when intent cannot be determined.
        
        Returns:
            A fallback message requesting clarification.
        """
        return (
            "🤔 I'm sorry, I didn't quite understand your question. "
            "Could you please clarify what you'd like to know? "
            "I can help with registration, contact information, schedules, and more."
        )


def handle_greeting(user_message: str) -> str:
    """
    Handles greeting messages from the user.
    
    Args:
        user_message: The user's input text.
        
    Returns:
        A friendly greeting response.
    """
    return GreetingHandler.handle(user_message)


def handle_fallback() -> str:
    """
    Provides a polite fallback response when intent cannot be determined.
    
    Returns:
        A fallback message requesting clarification.
    """
    return FallbackHandler.handle()


class ContextManager:
    """Manages conversation context and history."""
    
    MAX_HISTORY_LENGTH = 10
    
    @staticmethod
    def update(
        user_message: str, 
        context: ConversationContext, 
        detected_intent: Optional[Intent]
    ) -> ConversationContext:
        """
        Updates the conversation context based on the detected intent and user message.
        
        This maintains conversation continuity by tracking:
        - Current topic
        - Previous messages
        - Last interaction timestamp information
        
        Args:
            user_message: The user's input text.
            context: The existing conversation context.
            detected_intent: The detected intent from the user message.
            
        Returns:
            Updated conversation context.
        """
        # Track conversation history
        context.history.append({"user": user_message})
        
        # Limit history length for memory efficiency
        if len(context.history) > ContextManager.MAX_HISTORY_LENGTH:
            context.history = context.history[-ContextManager.MAX_HISTORY_LENGTH:]
        
        # Update current topic if intent is detected
        if detected_intent and detected_intent != Intent.FAREWELL:
            context.current_topic = detected_intent.value
            context.last_question = user_message
        elif detected_intent == Intent.FAREWELL:
            # Clear context on farewell, but preserve the history entry we just added
            context.current_topic = None
            context.last_question = None
            context.metadata = {}
            context.history = context.history[-1:] if context.history else []
        
        return context


def update_context(
    user_message: str, 
    context: Dict[str, Any], 
    detected_intent: Optional[str]
) -> Dict[str, Any]:
    """
    Updates the conversation context based on the detected intent and user message.
    
    This maintains conversation continuity by tracking:
    - Current topic
    - Previous messages
    - Last interaction timestamp information
    
    Args:
        user_message: The user's input text.
        context: The existing conversation context.
        detected_intent: The detected intent from the user message.
        
    Returns:
        Updated context dictionary.
    """
    ctx = ConversationContext.from_dict(context) if isinstance(context, dict) else context
    intent = Intent(detected_intent) if detected_intent else None
    updated_ctx = ContextManager.update(user_message, ctx, intent)
    return updated_ctx.to_dict()


class ConversationProcessor:
    """
    Main conversation processor that orchestrates the conversation management.
    
    This class handles the complete conversation flow:
    1. Intent detection
    2. Handler routing
    3. Context management
    4. Response generation
    """
    
    @staticmethod
    def process(user_message: str, context: ConversationContext) -> Tuple[str, ConversationContext]:
        """
        Processes the user input and returns chatbot response + updated context.
        
        Args:
            user_message: The latest text entered by the user.
            context: The conversation context.
            
        Returns:
            A tuple containing:
            - response: The chatbot's response string.
            - updated_context: The updated conversation context.
            
        Logic Flow:
            1. Detect user intent from keywords
            2. Route to appropriate handler based on intent
            3. Update conversation context
            4. Return response and updated context
        """
        logger.info(f"Processing user message: {user_message[:50]}...")
        
        # Handle empty input
        if not user_message or not user_message.strip():
            logger.debug("Empty message received, returning fallback")
            return FallbackHandler.handle(), context
        
        # Detect user intent from the message
        detected_intent = IntentDetector.detect(user_message)
        
        # Route to appropriate handler based on detected intent
        response = None
        
        if detected_intent == Intent.REGISTRATION:
            logger.debug("Routing to RegistrationHandler")
            response = RegistrationHandler.handle(user_message, context)
        
        elif detected_intent == Intent.CONTACT:
            logger.debug("Routing to ContactHandler")
            response = ContactHandler.handle(user_message, context)
        
        elif detected_intent == Intent.FAREWELL:
            logger.debug("Handling farewell intent")
            response = (
                "👋 Thank you for using FAIX AI Chatbot! "
                "Have a great day, and feel free to reach out anytime you need help!"
            )
        
        elif detected_intent is None:
            # Check if this is a greeting-like message
            greeting_keywords = ["hi", "hello", "hey", "greetings", "help"]
            is_greeting = (
                any(keyword in user_message.lower() for keyword in greeting_keywords) 
                and len(user_message) < 20
            )
            
            if is_greeting:
                logger.debug("Detected greeting message")
                response = GreetingHandler.handle(user_message)
            else:
                # If there's a previous context and current topic, try to maintain continuity
                if context.current_topic:
                    logger.debug(f"Maintaining context for topic: {context.current_topic}")
                    if context.current_topic == "registration":
                        response = RegistrationHandler.handle(user_message, context)
                    elif context.current_topic == "contact":
                        response = ContactHandler.handle(user_message, context)
                    else:
                        response = FallbackHandler.handle()
                else:
                    logger.debug("No context available, returning fallback")
                    response = FallbackHandler.handle()
        
        else:
            # Fallback for any unhandled intent
            logger.debug(f"Unhandled intent: {detected_intent}, returning fallback")
            response = FallbackHandler.handle()
        
        # Update context with the new interaction
        updated_context = ContextManager.update(user_message, context, detected_intent)
        
        # Add response to history for reference
        if len(updated_context.history) > 0:
            updated_context.history[-1]["bot"] = response
        else:
            # If history is empty, append a new entry with the bot response
            updated_context.history.append({"bot": response})
        
        logger.info(f"Generated response: {response[:50]}...")
        return response, updated_context


def process_conversation(user_message: str, context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Processes the user input, updates context, and returns chatbot response + updated context.
    
    This is the main function that orchestrates the conversation management module.
    
    Args:
        user_message: The latest text entered by the user.
        context: A dictionary that keeps track of current topic, last question, etc.
        
    Returns:
        A tuple containing:
        - response: The chatbot's response string.
        - updated_context: The updated conversation context dictionary.
        
    Logic Flow:
        1. Detect user intent from keywords
        2. Route to appropriate handler based on intent
        3. Update conversation context
        4. Return response and updated context
        
    Integration Notes:
        - Currently uses keyword-based intent detection
        - Can be extended with NLP intent classifier (e.g., from transformer models)
        - Can integrate with Knowledge Base module for retrieving specific information
        - Ready to be called from Django views in the web application
    """
    try:
        ctx = ConversationContext.from_dict(context) if isinstance(context, dict) else context
        response, updated_ctx = ConversationProcessor.process(user_message, ctx)
        return response, updated_ctx.to_dict()
    except Exception as e:
        logger.error(f"Error processing conversation: {e}", exc_info=True)
        # Return fallback response on error
        return FallbackHandler.handle(), context


# ============================================================================
# Test Section - Example Conversation Flow
# ============================================================================

if __name__ == "__main__":
    """
    Demonstrates the conversation manager with example conversation flows.
    """
    # Configure logging for tests
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    print("=" * 70)
    print("FAIX AI Chatbot - Conversation Manager Test")
    print("=" * 70)
    
    # Test Case 1: Registration flow
    print("\n📌 Test Case 1: Registration Topic Flow")
    print("-" * 70)
    context = {}
    messages_1 = [
        "Hi",
        "I want to register",
        "When is registration open?",
        "How about the form?",
        "Thank you"
    ]
    
    for msg in messages_1:
        reply, context = process_conversation(msg, context)
        print(f"User: {msg}")
        print(f"Bot: {reply}")
        print()
    
    # Test Case 2: Contact information flow
    print("\n📌 Test Case 2: Contact Information Flow")
    print("-" * 70)
    context = {}
    messages_2 = [
        "Hello",
        "Can I contact the registration office?",
        "What's their email?",
        "Bye"
    ]
    
    for msg in messages_2:
        reply, context = process_conversation(msg, context)
        print(f"User: {msg}")
        print(f"Bot: {reply}")
        print()
    
    # Test Case 3: Unclear input handling
    print("\n📌 Test Case 3: Fallback Response for Unclear Input")
    print("-" * 70)
    context = {}
    messages_3 = [
        "What about the weather?",
        "Tell me something random",
        "How do courses work?",  # Relates to registration topic
    ]
    
    for msg in messages_3:
        reply, context = process_conversation(msg, context)
        print(f"User: {msg}")
        print(f"Bot: {reply}")
        print()
    
    # Test Case 4: Context continuity
    print("\n📌 Test Case 4: Context Continuity Within Same Topic")
    print("-" * 70)
    context = {}
    messages_4 = [
        "I need help with registration",
        "How do I do it?",
        "What are the requirements?"
    ]
    
    for msg in messages_4:
        reply, context = process_conversation(msg, context)
        print(f"User: {msg}")
        print(f"Bot: {reply}")
        if "current_topic" in context:
            print(f"[Context - Current Topic: {context['current_topic']}]")
        print()
    
    # Test Case 5: Direct class usage (new API)
    print("\n📌 Test Case 5: Direct Class Usage (New API)")
    print("-" * 70)
    ctx = ConversationContext()
    messages_5 = [
        "Hello",
        "I have a question about courses",
        "Tell me more",
    ]
    
    for msg in messages_5:
        reply, ctx = ConversationProcessor.process(msg, ctx)
        print(f"User: {msg}")
        print(f"Bot: {reply}")
        print(f"[Context: {ctx.to_dict()}]")
        print()
    
    print("=" * 70)
    print("Test completed!")
    print("=" * 70)

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import uuid

class ContextManager:
    def __init__(self, context_dir: str = "context_history"):
        self.context_dir = context_dir
        self.current_session_id = None
        self.current_context = []
        self.max_context_length = 10  # Keep last 10 exchanges
        self.ensure_context_directory()
    
    def ensure_context_directory(self):
        """Ensure context directory exists"""
        if not os.path.exists(self.context_dir):
            os.makedirs(self.context_dir)
            print(f"Created context directory: {self.context_dir}")
    
    def start_new_session(self) -> str:
        """Start a new conversation session"""
        self.current_session_id = str(uuid.uuid4())
        self.current_context = []
        print(f"Started new session: {self.current_session_id}")
        return self.current_session_id
    
    def add_exchange(self, user_question: str, assistant_response: str, sources: List[Dict] = None):
        """Add a question-answer exchange to current context"""
        if not self.current_session_id:
            self.start_new_session()
        
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user_question": user_question,
            "assistant_response": assistant_response,
            "sources": sources or [],
            "exchange_id": len(self.current_context) + 1
        }
        
        self.current_context.append(exchange)
        
        # Keep only recent exchanges to avoid context overflow
        if len(self.current_context) > self.max_context_length:
            self.current_context = self.current_context[-self.max_context_length:]
        
        # Save to file
        self.save_session()
        print(f"Added exchange {exchange['exchange_id']} to session {self.current_session_id}")
    
    def get_context_summary(self) -> str:
        """Get a summary of recent conversation for context awareness"""
        if not self.current_context:
            return ""
        
        # Create a concise summary of recent exchanges
        context_summary = "RECENT CONVERSATION CONTEXT:\n"
        
        for exchange in self.current_context[-5:]:  # Last 5 exchanges
            context_summary += f"User asked: {exchange['user_question'][:100]}...\n"
            context_summary += f"Assistant answered about: {self.extract_key_topics(exchange['assistant_response'])}\n"
            context_summary += "---\n"
        
        return context_summary
    
    def extract_key_topics(self, response: str) -> str:
        """Extract key topics from assistant response"""
        # Look for section/article references
        import re
        
        topics = []
        
        # Extract sections and articles
        sections = re.findall(r'Section\s+\d+[A-Z]*', response, re.IGNORECASE)
        articles = re.findall(r'Article\s+\d+[A-Z]*', response, re.IGNORECASE)
        
        topics.extend(sections[:3])  # Max 3 sections
        topics.extend(articles[:3])  # Max 3 articles
        
        # Extract key legal terms
        legal_terms = re.findall(r'(income tax|tds|deduction|constitution|criminal law|rape|murder|theft|assessment|penalty)', response, re.IGNORECASE)
        topics.extend(list(set(legal_terms))[:3])  # Max 3 unique terms
        
        return ", ".join(topics) if topics else "general legal information"
    
    def get_contextual_query_variations(self, current_query: str) -> List[str]:
        """Generate query variations based on conversation context"""
        variations = [current_query]
        
        if not self.current_context:
            return variations
        
        # Analyze recent context for related topics
        recent_topics = []
        for exchange in self.current_context[-3:]:  # Last 3 exchanges
            topics = self.extract_key_topics(exchange['assistant_response'])
            recent_topics.extend(topics.split(", "))
        
        # Add contextual variations
        for topic in set(recent_topics):
            if topic and topic != "general legal information":
                variations.append(f"{current_query} {topic}")
                variations.append(f"{topic} related to {current_query}")
        
        return variations[:8]  # Limit variations
    
    def is_follow_up_question(self, question: str) -> bool:
        """Detect if current question is a follow-up to previous conversation"""
        if not self.current_context:
            return False
        
        follow_up_indicators = [
            "what about", "and what", "also tell", "more details", "explain further",
            "what if", "in that case", "similarly", "related to this", "about this",
            "can you elaborate", "more information", "tell me more", "what else",
            "in addition", "furthermore", "also", "additionally", "moreover"
        ]
        
        question_lower = question.lower()
        return any(indicator in question_lower for indicator in follow_up_indicators)
    
    def save_session(self):
        """Save current session to JSON file"""
        if not self.current_session_id or not self.current_context:
            return
        
        session_data = {
            "session_id": self.current_session_id,
            "created_at": self.current_context[0]["timestamp"] if self.current_context else datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "total_exchanges": len(self.current_context),
            "exchanges": self.current_context
        }
        
        file_path = os.path.join(self.context_dir, f"session_{self.current_session_id}.json")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving session: {str(e)}")
    
    def load_session(self, session_id: str) -> bool:
        """Load an existing session"""
        file_path = os.path.join(self.context_dir, f"session_{session_id}.json")
        
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            self.current_session_id = session_data["session_id"]
            self.current_context = session_data["exchanges"]
            print(f"Loaded session {session_id} with {len(self.current_context)} exchanges")
            return True
        except Exception as e:
            print(f"Error loading session: {str(e)}")
            return False
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """Get list of recent sessions"""
        sessions = []
        
        if not os.path.exists(self.context_dir):
            return sessions
        
        try:
            for filename in os.listdir(self.context_dir):
                if filename.startswith("session_") and filename.endswith(".json"):
                    file_path = os.path.join(self.context_dir, filename)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    sessions.append({
                        "session_id": session_data["session_id"],
                        "created_at": session_data["created_at"],
                        "last_updated": session_data["last_updated"],
                        "total_exchanges": session_data["total_exchanges"],
                        "preview": session_data["exchanges"][0]["user_question"][:100] if session_data["exchanges"] else "Empty session"
                    })
            
            # Sort by last updated
            sessions.sort(key=lambda x: x["last_updated"], reverse=True)
            return sessions[:limit]
        
        except Exception as e:
            print(f"Error getting recent sessions: {str(e)}")
            return []
    
    def clear_old_sessions(self, days_old: int = 30):
        """Clear sessions older than specified days"""
        if not os.path.exists(self.context_dir):
            return
        
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        try:
            for filename in os.listdir(self.context_dir):
                if filename.startswith("session_") and filename.endswith(".json"):
                    file_path = os.path.join(self.context_dir, filename)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    last_updated = datetime.fromisoformat(session_data["last_updated"])
                    
                    if last_updated < cutoff_date:
                        os.remove(file_path)
                        print(f"Removed old session: {filename}")
        
        except Exception as e:
            print(f"Error clearing old sessions: {str(e)}")
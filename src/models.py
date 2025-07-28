from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Set, Dict
from enum import Enum
import uuid


class MessageType(Enum):
    USER_INPUT = "user_input"
    AGENT_RESPONSE = "agent_response"
    SYSTEM_UPDATE = "system_update"


@dataclass
class Message:
    content: str
    timestamp: datetime
    user_name: str
    message_type: MessageType
    user_identifier: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "user_name": self.user_name,
            "message_type": self.message_type.value,
            "user_identifier": self.user_identifier
        }


@dataclass
class Participant:
    name: str
    address: str = ""
    food_preferences: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    user_identifier: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "address": self.address,
            "food_preferences": self.food_preferences,
            "constraints": self.constraints,
            "timestamp": self.timestamp.isoformat(),
            "user_identifier": self.user_identifier
        }
    
    def get_summary(self) -> str:
        prefs = ", ".join(self.food_preferences) if self.food_preferences else "no specific preferences"
        constraints_str = f" ({', '.join(self.constraints)})" if self.constraints else ""
        return f"{self.name} from {self.address} - likes {prefs}{constraints_str}"


@dataclass
class HangoutPlan:
    venue_recommendation: str
    reasoning_chain: str
    alternatives: List[str] = field(default_factory=list)
    participant_analysis: str = ""
    contributor_summary: str = ""
    confidence_level: str = "Low"  # Low, Medium, High
    version: int = 1
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "venue_recommendation": self.venue_recommendation,
            "reasoning_chain": self.reasoning_chain,
            "alternatives": self.alternatives,
            "participant_analysis": self.participant_analysis,
            "contributor_summary": self.contributor_summary,
            "confidence_level": self.confidence_level,
            "version": self.version,
            "generated_at": self.generated_at.isoformat()
        }


@dataclass
class Session:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    participants: List[Participant] = field(default_factory=list)
    conversation_history: List[Message] = field(default_factory=list)
    current_plan: Optional[HangoutPlan] = None
    finalized_plan: Optional[HangoutPlan] = None
    created_at: datetime = field(default_factory=datetime.now)
    active_users: Set[str] = field(default_factory=set)
    state: str = "collecting_info"  # collecting_info, plan_ready, finalized
    
    def add_participant(self, participant: Participant) -> bool:
        """Add or update a participant. Returns True if new, False if updated."""
        for i, p in enumerate(self.participants):
            if p.name.lower() == participant.name.lower():
                # Update existing participant
                self.participants[i] = participant
                return False
        
        # Add new participant
        self.participants.append(participant)
        return True
    
    def get_participant_count(self) -> int:
        return len(self.participants)
    
    def get_active_participants(self) -> List[Participant]:
        return [p for p in self.participants if p.user_identifier in self.active_users]
    
    def add_message(self, message: Message):
        self.conversation_history.append(message)
        if message.user_identifier:
            self.active_users.add(message.user_identifier)
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "participants": [p.to_dict() for p in self.participants],
            "conversation_history": [m.to_dict() for m in self.conversation_history[-20:]],  # Last 20 messages
            "current_plan": self.current_plan.to_dict() if self.current_plan else None,
            "finalized_plan": self.finalized_plan.to_dict() if self.finalized_plan else None,
            "created_at": self.created_at.isoformat(),
            "active_users": list(self.active_users),
            "state": self.state,
            "participant_count": self.get_participant_count()
        }
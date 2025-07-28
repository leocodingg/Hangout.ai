import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

from .models import Session, Participant, Message, MessageType, HangoutPlan
from .nemotron_client import NemotronClient
from .maps_client import GoogleMapsClient

logger = logging.getLogger(__name__)


class HangoutOrchestrator:
    """Main orchestrator for hangout planning using NVIDIA Nemo Agent Toolkit patterns."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.nemotron = NemotronClient()
        self.maps_client = GoogleMapsClient()
        self.session = self._load_or_create_session(session_id)
        
        # Keywords that trigger plan finalization
        self.finalization_triggers = [
            "finalize", "make a plan", "make plan", "let's decide", 
            "create plan", "generate plan", "what's the plan", "decide"
        ]
    
    def _load_or_create_session(self, session_id: str) -> Session:
        """Load existing session or create new one."""
        # In production, this would load from a database
        # For now, we create a new session
        return Session(session_id=session_id)
    
    def _should_finalize_plan(self, message: str) -> bool:
        """Check if the message contains plan finalization triggers."""
        message_lower = message.lower()
        return any(trigger in message_lower for trigger in self.finalization_triggers)
    
    def _extract_participant_info(self, user_message: str, user_name: str) -> Optional[Participant]:
        """Extract participant information from user message."""
        # Get existing participant info if updating
        existing_participant = None
        for p in self.session.participants:
            if p.name.lower() == user_name.lower():
                existing_participant = p
                break
        
        existing_context = ""
        if existing_participant:
            existing_context = f"Existing info: {existing_participant.get_summary()}"
        
        # Use Nemotron to extract information
        extracted = self.nemotron.extract_participant_info(user_message, existing_context)
        
        if not extracted or not extracted.get('name'):
            return None
        
        # Create participant object
        participant = Participant(
            name=extracted.get('name', user_name),
            address=extracted.get('address', ''),
            food_preferences=extracted.get('food_preferences', []),
            constraints=extracted.get('constraints', []),
            user_identifier=user_name
        )
        
        # Geocode address if provided
        if participant.address and self.maps_client.is_available():
            geocoded = self.maps_client.geocode_address(participant.address)
            if geocoded:
                participant.address = geocoded
        
        return participant
    
    def _generate_plan(self) -> Optional[HangoutPlan]:
        """Generate or update the hangout plan based on current participants."""
        if len(self.session.participants) < 2:
            return None
        
        # Convert participants to dict format for Nemotron
        participants_data = [p.to_dict() for p in self.session.participants]
        
        # Get previous plan if exists
        previous_plan_data = None
        if self.session.current_plan:
            previous_plan_data = self.session.current_plan.to_dict()
        
        # Generate plan using Nemotron
        plan_data = self.nemotron.generate_hangout_plan(participants_data, previous_plan_data)
        
        if not plan_data or not plan_data.get('venue_recommendation'):
            return None
        
        # Create HangoutPlan object
        version = 1
        if self.session.current_plan:
            version = self.session.current_plan.version + 1
        
        plan = HangoutPlan(
            venue_recommendation=plan_data.get('venue_recommendation', ''),
            reasoning_chain=plan_data.get('reasoning_chain', ''),
            alternatives=plan_data.get('alternatives', []),
            participant_analysis=plan_data.get('participant_analysis', ''),
            contributor_summary=plan_data.get('contributor_summary', ''),
            confidence_level=plan_data.get('confidence_level', 'Low'),
            version=version
        )
        
        return plan
    
    def process_message(self, user_message: str, user_name: str, user_id: str) -> Tuple[str, Optional[Dict]]:
        """
        Process a user message and return response + optional plan update.
        
        Returns:
            Tuple of (response_message, plan_update_dict or None)
        """
        # Add user message to history
        user_msg = Message(
            content=user_message,
            timestamp=datetime.now(),
            user_name=user_name,
            message_type=MessageType.USER_INPUT,
            user_identifier=user_id
        )
        self.session.add_message(user_msg)
        
        # Check for plan finalization request
        should_finalize = self._should_finalize_plan(user_message)
        
        # Extract participant information
        participant = self._extract_participant_info(user_message, user_name)
        is_new_participant = False
        
        if participant:
            is_new_participant = self.session.add_participant(participant)
            
            # Log the update
            if is_new_participant:
                logger.info(f"New participant added: {participant.name}")
            else:
                logger.info(f"Updated participant info: {participant.name}")
        
        # Generate conversational response
        conversation_context = [m.to_dict() for m in self.session.conversation_history[-20:]]
        response = self.nemotron.process_conversation(user_message, conversation_context)
        
        # Add specific confirmations if we extracted participant info
        if participant:
            if is_new_participant:
                response += f"\n\nGot it! Added **{participant.name}** "
            else:
                response += f"\n\nUpdated info for **{participant.name}** "
            
            if participant.address:
                response += f"from {participant.address}"
            if participant.food_preferences:
                response += f" who likes {', '.join(participant.food_preferences)}"
            if participant.constraints:
                response += f" ({', '.join(participant.constraints)})"
            response += "."
        
        # Generate or update plan if we have participant info
        plan_update = None
        if participant and len(self.session.participants) >= 2:
            new_plan = self._generate_plan()
            if new_plan:
                self.session.current_plan = new_plan
                plan_update = new_plan.to_dict()
                
                # Add plan update notification
                participant_names = [p.name for p in self.session.participants]
                response += f"\n\n🎯 **Plan Updated (v{new_plan.version})**: Now optimizing for {len(self.session.participants)} people ({', '.join(participant_names)})!"
                
                if new_plan.confidence_level == "High":
                    response += " We have a great recommendation ready!"
                elif new_plan.confidence_level == "Medium":
                    response += " Good options available."
                else:
                    response += " Still gathering info for best recommendations."
        
        # Handle finalization request
        if should_finalize and self.session.current_plan:
            self.session.finalized_plan = self.session.current_plan
            self.session.state = "finalized"
            response += "\n\n✅ **Plan Finalized!** The current recommendation has been locked in."
        elif should_finalize and not self.session.current_plan:
            response = "We need at least 2 participants before I can create a plan. Who else is joining?"
        
        # Add agent response to history
        agent_msg = Message(
            content=response,
            timestamp=datetime.now(),
            user_name="Hangout AI",
            message_type=MessageType.AGENT_RESPONSE,
            user_identifier="system"
        )
        self.session.add_message(agent_msg)
        
        return response, plan_update
    
    def get_session_state(self) -> Dict:
        """Get current session state for display."""
        return self.session.to_dict()
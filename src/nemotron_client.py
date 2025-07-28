import os
import json
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class NemotronClient:
    """Client for interacting with NVIDIA's Nemotron LLM API."""
    
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY")
        self.api_endpoint = os.getenv("NVIDIA_API_ENDPOINT", "https://api.nvcf.nvidia.com/v2/nvcf/pexec/functions/")
        self.model_id = "nvidia/nemotron-4-340b-instruct"  # Using Nemotron-4 340B model
        
        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY not found in environment variables")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1000) -> Dict:
        """Make a request to the Nemotron API."""
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 0.9,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stream": False
        }
        
        url = f"{self.api_endpoint}{self.model_id}"
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Nemotron API request failed: {e}")
            raise
    
    def extract_participant_info(self, user_message: str, existing_context: str = "") -> Dict:
        """Extract participant information from a user message."""
        system_prompt = """You are an AI assistant helping to extract participant information for hangout planning.
        
Extract the following information from the user's message:
- Name: The person's name
- Address/Location: Where they're located (neighborhood, city, or specific address)
- Food Preferences: What types of food they like
- Constraints: Any dietary restrictions, budget limits, or other constraints

Return the information as a JSON object. If information is not provided, use null for that field.
If this seems to be updating existing information, note what's being updated.

Example output:
{
    "name": "Sarah",
    "address": "Brooklyn, NY",
    "food_preferences": ["sushi", "Thai food"],
    "constraints": ["vegetarian"],
    "is_update": false
}"""
        
        user_prompt = f"Extract participant information from this message: \"{user_message}\""
        if existing_context:
            user_prompt += f"\n\nExisting context: {existing_context}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self._make_request(messages, temperature=0.3)
        
        try:
            content = response['choices'][0]['message']['content']
            # Extract JSON from the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                logger.error(f"No JSON found in response: {content}")
                return {}
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse extraction response: {e}")
            return {}
    
    def generate_hangout_plan(self, participants: List[Dict], previous_plan: Optional[Dict] = None) -> Dict:
        """Generate an optimized hangout plan based on participant information."""
        system_prompt = """You are an AI assistant that creates optimized hangout plans for groups.
        
Consider:
1. Geographic center point based on all participants' locations
2. Food preferences and how to accommodate everyone
3. Dietary restrictions and constraints
4. Travel distance fairness
5. Venue type that works for the group size

Provide:
1. A primary venue recommendation with full reasoning
2. 2-3 alternative options
3. Clear explanation of trade-offs made
4. Confidence level (Low/Medium/High) based on participant count and preference alignment

Format your response as JSON with these fields:
{
    "venue_recommendation": "Restaurant Name - Location",
    "reasoning_chain": "Step by step reasoning...",
    "alternatives": ["Alt 1", "Alt 2", "Alt 3"],
    "participant_analysis": "How each person's needs are met...",
    "contributor_summary": "Based on input from [names]...",
    "confidence_level": "Medium"
}"""
        
        # Build participant summary
        participant_summaries = []
        for p in participants:
            summary = f"- {p['name']} from {p['address']}"
            if p.get('food_preferences'):
                summary += f", likes {', '.join(p['food_preferences'])}"
            if p.get('constraints'):
                summary += f", constraints: {', '.join(p['constraints'])}"
            participant_summaries.append(summary)
        
        user_prompt = f"Generate a hangout plan for {len(participants)} participants:\n\n"
        user_prompt += "\n".join(participant_summaries)
        
        if previous_plan:
            user_prompt += f"\n\nPrevious plan (version {previous_plan.get('version', 1)}): {previous_plan.get('venue_recommendation')}"
            user_prompt += "\n\nExplain what changed and why with the new participant data."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self._make_request(messages, temperature=0.5, max_tokens=1500)
        
        try:
            content = response['choices'][0]['message']['content']
            # Extract JSON from the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                logger.error(f"No JSON found in response: {content}")
                return {
                    "venue_recommendation": "Unable to generate recommendation",
                    "reasoning_chain": content,
                    "alternatives": [],
                    "confidence_level": "Low"
                }
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse plan response: {e}")
            return {
                "venue_recommendation": "Error generating plan",
                "reasoning_chain": str(e),
                "alternatives": [],
                "confidence_level": "Low"
            }
    
    def process_conversation(self, user_message: str, conversation_context: List[Dict]) -> str:
        """Process a conversation message and generate appropriate response."""
        system_prompt = """You are a friendly AI assistant helping groups plan hangouts together.
        
Your goals:
1. Welcome new participants warmly
2. Extract their information naturally (name, location, food preferences)
3. Confirm what you understood
4. Let them know when plans are being updated
5. Be conversational but concise

When you detect planning triggers (like "finalize", "make a plan", "let's decide"), acknowledge it."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation context (last 10 messages)
        for msg in conversation_context[-10:]:
            role = "user" if msg.get("message_type") == "user_input" else "assistant"
            messages.append({"role": role, "content": msg.get("content", "")})
        
        messages.append({"role": "user", "content": user_message})
        
        response = self._make_request(messages, temperature=0.8, max_tokens=500)
        
        try:
            return response['choices'][0]['message']['content']
        except KeyError:
            return "I'm here to help plan your hangout! Please tell me your name and where you're located."
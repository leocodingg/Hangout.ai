import streamlit as st
import uuid
import os
from datetime import datetime
import sys
import logging

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from orchestrator import HangoutOrchestrator
from models import MessageType
from map_component import InteractiveMapComponent
from maps_client import GoogleMapsClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Hangout Orchestrator AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())[:8]
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'maps_client' not in st.session_state:
        st.session_state.maps_client = GoogleMapsClient()
    if 'map_component' not in st.session_state:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if api_key and api_key != "your_google_maps_key_here":
            st.session_state.map_component = InteractiveMapComponent(api_key)
        else:
            st.session_state.map_component = None

def create_new_session():
    """Create a new hangout planning session."""
    session_id = str(uuid.uuid4())[:8]
    st.session_state.session_id = session_id
    st.session_state.orchestrator = HangoutOrchestrator(session_id)
    st.session_state.messages = []
    return session_id

def join_session(session_id: str):
    """Join an existing hangout planning session."""
    st.session_state.session_id = session_id
    st.session_state.orchestrator = HangoutOrchestrator(session_id)
    # Load existing messages from session
    if st.session_state.orchestrator.session.conversation_history:
        st.session_state.messages = [
            {
                "role": "user" if msg.message_type == MessageType.USER_INPUT else "assistant",
                "content": msg.content,
                "user_name": msg.user_name,
                "timestamp": msg.timestamp
            }
            for msg in st.session_state.orchestrator.session.conversation_history
        ]

def display_session_sidebar():
    """Display session information in the sidebar."""
    with st.sidebar:
        st.header("Session Info")
        
        if st.session_state.session_id:
            st.success(f"**Session ID:** `{st.session_state.session_id}`")
            
            # Share link
            query_params = st.query_params
            share_url = f"?session={st.session_state.session_id}"
            st.code(share_url, language="text")
            st.caption("Share this link with friends!")
            
            # Get session state
            if st.session_state.orchestrator:
                session_data = st.session_state.orchestrator.get_session_state()
                
                # Participants
                st.subheader("Participants")
                if session_data['participants']:
                    for p in session_data['participants']:
                        st.write(f"**{p['name']}**")
                        if p['address']:
                            st.caption(f"Location: {p['address']}")
                        if p['food_preferences']:
                            st.caption(f"Preferences: {', '.join(p['food_preferences'])}")
                        if p['constraints']:
                            st.caption(f"Constraints: {', '.join(p['constraints'])}")
                        st.divider()
                else:
                    st.info("No participants yet")
                
                # Current plan
                if session_data.get('current_plan'):
                    st.subheader("Current Plan")
                    plan = session_data['current_plan']
                    st.success(f"**v{plan['version']}** - {plan['confidence_level']} confidence")
                    
                    with st.expander("View Plan Details"):
                        st.write(f"**Recommendation:** {plan['venue_recommendation']}")
                        st.write(f"**Reasoning:** {plan['reasoning_chain']}")
                        if plan['alternatives']:
                            st.write("**Alternatives:**")
                            for alt in plan['alternatives']:
                                st.write(f"- {alt}")
        
        # Session controls
        st.header("Controls")
        
        if st.button("New Session"):
            create_new_session()
            st.rerun()
        
        if st.button("Refresh"):
            st.rerun()

def display_chat_interface():
    """Display the main chat interface."""
    st.header("Hangout Planning Chat")
    
    # Check if user needs to enter name
    if not st.session_state.user_name:
        st.info("Welcome! Please enter your name to start planning.")
        user_name = st.text_input("Your name:", key="name_input")
        if st.button("Join Chat") and user_name:
            st.session_state.user_name = user_name
            st.rerun()
        return
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(f"**{message.get('user_name', 'User')}:** {message['content']}")
                else:
                    st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        user_message = {
            "role": "user",
            "content": prompt,
            "user_name": st.session_state.user_name,
            "timestamp": datetime.now()
        }
        st.session_state.messages.append(user_message)
        
        # Process message with orchestrator
        if st.session_state.orchestrator:
            try:
                with st.spinner("Planning your hangout..."):
                    response, plan_update = st.session_state.orchestrator.process_message(
                        prompt, 
                        st.session_state.user_name, 
                        st.session_state.user_id
                    )
                
                # Add assistant response to chat
                assistant_message = {
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                }
                st.session_state.messages.append(assistant_message)
                
                # If there's a plan update, show notification
                if plan_update:
                    st.success("Plan updated! Check the sidebar for details.")
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                st.error("Sorry, I'm having trouble processing your message. Please try again.")
        
        # Rerun to update the chat
        st.experimental_rerun()

def display_interactive_map(participants, venues=None):
    """Display the interactive map with participants and venues."""
    if not st.session_state.map_component:
        st.warning("Interactive map not available. Please add your Google Maps API key to .env file.")
        return
    
    venues = venues or []
    
    # Get coordinates for participants
    participant_coords = st.session_state.map_component.get_participant_coordinates(
        participants, st.session_state.maps_client
    )
    
    # Get coordinates for venues if available
    venue_coords = []
    if venues:
        venue_coords = st.session_state.map_component.get_venue_coordinates(
            venues, st.session_state.maps_client
        )
    
    # Calculate center point
    all_coords = []
    for p in participant_coords:
        if p['lat'] and p['lng']:
            all_coords.append((p['lat'], p['lng']))
    for v in venue_coords:
        if v['lat'] and v['lng']:
            all_coords.append((v['lat'], v['lng']))
    
    if all_coords:
        center_lat = sum(coord[0] for coord in all_coords) / len(all_coords)
        center_lng = sum(coord[1] for coord in all_coords) / len(all_coords)
        center = (center_lat, center_lng)
    else:
        center = (37.7749, -122.4194)  # Default to SF
    
    # Render the map
    st.session_state.map_component.render_map(
        participants=participant_coords,
        venues=venue_coords,
        center=center,
        zoom=12
    )

def display_plan_view():
    """Display the current plan in detail."""
    if not st.session_state.orchestrator:
        st.info("Join a session to see the plan!")
        return
    
    session_data = st.session_state.orchestrator.get_session_state()
    current_plan = session_data.get('current_plan')
    finalized_plan = session_data.get('finalized_plan')
    participants = session_data.get('participants', [])
    
    if finalized_plan:
        st.success("✅ **Plan Finalized!**")
        plan = finalized_plan
    elif current_plan:
        st.info(f"📋 **Current Plan (v{current_plan['version']})**")
        plan = current_plan
    else:
        st.warning("No plan available yet. Need at least 2 participants!")
        # Still show map with participants if available
        if participants and st.session_state.map_component:
            st.subheader("🗺️ Participant Locations")
            display_interactive_map(participants, [])
        return
    
    # Main recommendation
    st.subheader("🎯 Recommendation")
    st.write(f"**{plan['venue_recommendation']}**")
    
    # Interactive Map
    if st.session_state.map_component and participants:
        st.subheader("🗺️ Interactive Map")
        st.caption("🔵 Participants • 🟠 Recommended Venues")
        
        # Try to get venue data from the orchestrator if available
        venues = []
        if hasattr(st.session_state.orchestrator, 'maps_client') and st.session_state.orchestrator.maps_client:
            # Get center point for venue search
            center = st.session_state.orchestrator.maps_client.find_geographic_center(
                [p.get('address', '') for p in participants if p.get('address')]
            )
            if center:
                venues = st.session_state.orchestrator.maps_client.search_nearby_venues(
                    center, "restaurant", 2000
                )
        
        display_interactive_map(participants, venues)
    
    # Reasoning
    st.subheader("🧠 AI Reasoning")
    st.write(plan['reasoning_chain'])
    
    # Participant analysis
    if plan.get('participant_analysis'):
        st.subheader("👥 How This Works for Everyone")
        st.write(plan['participant_analysis'])
    
    # Contributors
    if plan.get('contributor_summary'):
        st.subheader("👏 Based On Input From")
        st.write(plan['contributor_summary'])
    
    # Alternatives
    if plan.get('alternatives'):
        st.subheader("🔄 Alternative Options")
        for i, alt in enumerate(plan['alternatives'], 1):
            st.write(f"{i}. {alt}")
    
    # Confidence and metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        confidence_color = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}
        st.metric("Confidence", f"{confidence_color.get(plan['confidence_level'], '⚪')} {plan['confidence_level']}")
    with col2:
        st.metric("Version", plan['version'])
    with col3:
        st.metric("Participants", len(session_data['participants']))

def main():
    """Main application function."""
    init_session_state()
    
    st.title("🎯 Hangout Orchestrator AI")
    st.caption("Powered by NVIDIA Nemotron LLM • Plan hangouts with friends through natural conversation")
    
    # Check for session parameter in URL
    query_params = st.query_params
    if 'session' in query_params and not st.session_state.session_id:
        session_id = query_params['session'][0]
        join_session(session_id)
    
    # Create session if none exists
    if not st.session_state.session_id:
        st.info("👋 Welcome! Start a new hangout planning session or join an existing one.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🆕 Start New Session", use_container_width=True):
                session_id = create_new_session()
                st.success(f"Created session: {session_id}")
                st.rerun()
        
        with col2:
            session_input = st.text_input("Enter session ID to join:")
            if st.button("🔗 Join Session", use_container_width=True) and session_input:
                join_session(session_input.strip())
                st.rerun()
        
        return
    
    # Display sidebar
    display_session_sidebar()
    
    # Main content tabs
    tab1, tab2 = st.tabs(["💬 Chat", "📋 Plan"])
    
    with tab1:
        display_chat_interface()
    
    with tab2:
        display_plan_view()

if __name__ == "__main__":
    main()
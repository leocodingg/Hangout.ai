# Hangout Orchestrator AI

*A collaborative AI agent powered by NVIDIA Nemotron LLM that helps groups plan hangouts through natural conversation.*

Built for the **NVIDIA Nemo Toolkit Hackathon** - showcasing intelligent conversation management and multi-participant planning optimization.

## Quick Start (One-Click Deploy)

### Prerequisites
- Python 3.8+
- NVIDIA API Key ([Get one here](https://developer.nvidia.com/))
- Google Maps API Key (optional, for location services)

### 1. Clone & Install
```bash
git clone https://github.com/your-username/hangout-orchestrator.git
cd hangout-orchestrator
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys:
# NVIDIA_API_KEY=your_nvidia_api_key_here
# GOOGLE_MAPS_API_KEY=your_google_maps_key_here
```

### 3. Run the App
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` with shareable session links ready to use!

## Live Demo Flow

### Scenario: San Francisco Friends
Try this demo scenario with 3+ people:

1. **Person 1:** "Hey! I'm Alex from Mission District, I love Italian food but I'm vegetarian"
2. **Person 2:** "Jordan here! I live in Marina District and prefer Asian cuisine, no dietary restrictions"  
3. **Person 3:** "Casey from Castro District - I love Mexican food but I'm dairy-free"
4. **Anyone:** "Okay let's finalize the plan!"

Watch the AI:
- Extract participant info automatically
- Calculate geographic center points
- Balance conflicting food preferences  
- Generate optimized venue recommendations
- Show transparent reasoning chains

## How It Works

### NVIDIA Nemotron LLM Powers:
- **Information Extraction**: Converts "I'm Sarah from Brooklyn, love sushi" → structured participant data
- **Plan Optimization**: Multi-step reasoning for location, preferences, and constraints
- **Conversation Management**: Natural, contextual responses with progress updates

### Nemo Agent Toolkit Integration:
- **Session Management**: Persistent multi-user conversations
- **Tool Orchestration**: Coordinates LLM + Maps API + state management
- **Real-time Updates**: Live plan regeneration as participants join

### Architecture Overview
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    Hangout       │    │   Nemotron      │
│   Frontend      │◄──►│  Orchestrator    │◄──►│   LLM Client    │
│                 │    │                  │    │                 │
└─────────────────┘    └─────────┬────────┘    └─────────────────┘
                                 │
                       ┌─────────▼────────┐
                       │  Google Maps     │
                       │     Client       │
                       └──────────────────┘
```

## Key Features

### Conversational Planning
- No forms or structured input required
- Natural language: "I'm Mike from downtown, love Thai but vegetarian"
- Multi-turn conversations with context retention

### Live Plan Updates  
- **Automatic regeneration** when new participants join
- **Version tracking**: Plan v1 → v2 → v3 as group grows
- **Confidence indicators**: Low/Medium/High based on participant count

### Multi-User Sessions
- **Shareable links**: `/app?session=abc123`
- **Real-time participation**: See who joined and their preferences
- **Message attribution**: Know who said what

### Transparent AI Reasoning
- Step-by-step plan optimization logic
- Geographic center point calculations
- Preference conflict resolution strategies
- Alternative venue suggestions

## Project Structure

```
hangout-orchestrator/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment configuration template
├── src/
│   ├── models.py            # Data models (Session, Participant, etc.)
│   ├── orchestrator.py      # Main AI orchestrator class
│   ├── nemotron_client.py   # NVIDIA Nemotron LLM client
│   └── maps_client.py       # Google Maps API integration
├── tests/                   # Test files (coming soon)
└── docs/                    # Additional documentation
```

## Configuration

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `NVIDIA_API_KEY` | Yes | Your NVIDIA API key for Nemotron access |
| `GOOGLE_MAPS_API_KEY` | No | Google Maps API key (fallback without maps) |
| `APP_HOST` | No | Host address (default: 0.0.0.0) |
| `APP_PORT` | No | Port number (default: 8501) |

### Nemotron Model Configuration
- **Model**: `nvidia/nemotron-4-340b-instruct`
- **Context Window**: Optimized for multi-turn conversations
- **Temperature**: Adaptive (0.3 for extraction, 0.8 for conversation)

## Demo Scenarios

### Urban Planning Challenge
```
Alex (Brooklyn): "Italian food lover, vegetarian, budget-conscious"
Jordan (Manhattan): "Sushi preference, mobile, expense account"  
River (Queens): "Vegetarian, public transit only"
Casey (Bronx): "Italian food, has car"
```

**Expected AI Logic**: *"Manhattan is most transit-accessible for River. Budget constraint suggests casual dining. Sushi vs Italian conflict resolved by Mediterranean options that satisfy both vegetarian requirements..."*

### Cross-City Groups
Test the AI's geographic reasoning with participants from:
- Different neighborhoods (SF: Mission, Marina, Castro)
- Different cities (NYC boroughs)
- Different transportation constraints

## Production Deployment

### Streamlit Cloud
```bash
# Add to Streamlit Cloud:
# Repository: your-repo-url
# Branch: main  
# Main file: app.py
# Add secrets: NVIDIA_API_KEY, GOOGLE_MAPS_API_KEY
```

### Docker (Coming Soon)
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## Development

### Adding New Features
1. **New extraction capabilities**: Modify `nemotron_client.py::extract_participant_info()`
2. **Enhanced planning logic**: Update `nemotron_client.py::generate_hangout_plan()`
3. **UI improvements**: Edit `app.py` Streamlit components

### Testing with Mock Data
```python
# Test participant extraction
participant = orchestrator._extract_participant_info(
    "I'm Sarah from Brooklyn Heights, love sushi and ramen",
    "Sarah"
)
print(participant.get_summary())
```

## Hackathon Criteria

### NVIDIA Technology Usage
- **Nemotron LLM**: Core reasoning and extraction engine
- **Nemo Toolkit Patterns**: Conversation management architecture
- **API Integration**: Production-ready NVIDIA API client

### Technical Sophistication  
- **Multi-step reasoning**: Geographic + preference + constraint optimization
- **State management**: Persistent multi-user sessions
- **Real-time updates**: Live plan regeneration
- **Error handling**: Graceful API failure management

### Practical Application
- **Real-world usage**: Judges can actively test during presentation
- **Scalable design**: Session-based architecture supports concurrent users
- **Professional quality**: Production-ready code with documentation

## Troubleshooting

### Common Issues

**"NVIDIA API Key not found"**
```bash
# Check your .env file exists and has the correct key
cat .env | grep NVIDIA_API_KEY
```

**"Module not found errors"**
```bash
# Install dependencies
pip install -r requirements.txt
# Add src to Python path
export PYTHONPATH="${PYTHONPATH}:./src"
```

**"Streamlit sharing errors"**  
```bash
# Use experimental_get_query_params() for older Streamlit versions
# Update Streamlit: pip install streamlit==1.32.0
```

### Debug Mode
```bash
# Run with debug logging
STREAMLIT_LOGGER_LEVEL=debug streamlit run app.py
```

## Roadmap

### Phase 2 Enhancements
- [ ] **Calendar Integration**: Google Calendar availability checking
- [ ] **Budget Optimization**: Price filtering and cost splitting
- [ ] **Activity Planning**: Beyond restaurants - events, entertainment
- [ ] **Persistent Storage**: Database backend for production scale

### Advanced AI Features
- [ ] **Multi-step Planning**: Day-long itinerary generation  
- [ ] **Group Dynamics**: Personality-based recommendation weighting
- [ ] **Learning System**: Improve from successful hangout patterns

## License

MIT License - Feel free to fork and enhance!

## Acknowledgments

- **NVIDIA** for Nemotron LLM and Nemo Toolkit
- **Streamlit** for rapid prototyping framework  
- **Google Maps** for geographic intelligence

---

*Built for the NVIDIA Nemo Toolkit Hackathon*

**Demo Ready**: Clone, configure, and start planning hangouts in under 5 minutes!
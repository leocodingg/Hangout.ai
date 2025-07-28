#!/bin/bash

# Hangout Orchestrator AI - brev.dev setup script
echo "🎯 Setting up Hangout Orchestrator AI on brev.dev..."

# Update system packages
sudo apt-get update

# Install Python 3.9+ if not available
python3 --version || sudo apt-get install -y python3 python3-pip

# Install project dependencies
pip3 install -r requirements.txt

# Create .env from template if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📝 Created .env file - please add your NVIDIA_API_KEY"
fi

# Set up Streamlit configuration
mkdir -p ~/.streamlit
cat > ~/.streamlit/config.toml << EOF
[server]
port = 8501
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
EOF

echo "✅ Setup complete!"
echo "🚀 Run: streamlit run app.py"
echo "🔑 Remember to set your NVIDIA_API_KEY in the environment variables"
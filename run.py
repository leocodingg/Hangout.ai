#!/usr/bin/env python3
"""
Quick start script for Hangout Orchestrator AI
NVIDIA Nemo Toolkit Hackathon Project
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        print("📝 Copy .env.example to .env and add your API keys")
        return False
    
    with open(env_path) as f:
        content = f.read()
        
    if "NVIDIA_API_KEY=" not in content or "NVIDIA_API_KEY=your_nvidia_api_key_here" in content:
        print("❌ NVIDIA_API_KEY not configured in .env")
        print("🔑 Get your API key from: https://developer.nvidia.com/")
        return False
    
    print("✅ Environment configured")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_app():
    """Run the Streamlit app"""
    print("\n🚀 Starting Hangout Orchestrator AI...")
    print("📱 Access at: http://localhost:8501")
    print("🔗 Share session links with friends to plan together!")
    print("\n💡 Demo: Say 'Hi I'm [Name] from [Location], I like [Food]'")
    print("🎯 Then have friends join and say 'finalize the plan' when ready\n")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Hangout Orchestrator stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start app: {e}")

def main():
    """Main setup and run function"""
    print("🎯 Hangout Orchestrator AI - NVIDIA Nemo Toolkit")
    print("=" * 50)
    
    if not check_python_version():
        return 1
    
    if not check_env_file():
        return 1
    
    if not install_dependencies():
        return 1
    
    run_app()
    return 0

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Quick start script for Automobile Sales Forecasting Streamlit App
Run: python run_app.py
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ ERROR: Python 3.8+ is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import streamlit
        import pandas
        import joblib
        import lightgbm
        return True
    except ImportError:
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing required packages...")
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def run_streamlit_app():
    """Run the Streamlit application"""
    app_file = Path(__file__).parent / "streamlit_app.py"
    
    print("\n" + "="*50)
    print("🚗 Automobile Sales Forecasting System")
    print("="*50)
    print("\n🌐 Opening app at: http://localhost:8501")
    print("📊 Press Ctrl+C to stop the application\n")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(app_file)],
            check=False
        )
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    os.chdir(Path(__file__).parent)
    
    # Check Python version
    if not check_python():
        sys.exit(1)
    
    # Check and install dependencies
    if not check_dependencies():
        print("📥 Installing dependencies...")
        if not install_dependencies():
            sys.exit(1)
    else:
        print("✅ All dependencies are already installed")
    
    # Run the app
    run_streamlit_app()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

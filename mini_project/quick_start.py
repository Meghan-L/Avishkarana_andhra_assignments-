#!/usr/bin/env python
"""
QUICK START GUIDE - Run this file to set everything up and execute the complete pipeline
Usage: python quick_start.py
"""

import subprocess
import sys
import os
import platform

def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"▶ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - SUCCESS\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}\n")
        return False

def main():
    """Main quick start routine."""
    
    print_header("🚀 DUAL-ENGINE RETAIL FORECASTING SYSTEM - QUICK START")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"❌ Python 3.8+ required. You have Python {python_version.major}.{python_version.minor}")
        sys.exit(1)
    
    print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Step 1: Install dependencies
    print_header("STEP 1: Installing Python Dependencies")
    
    if platform.system() == "Windows":
        pip_cmd = "pip install -r requirements.txt"
    else:
        pip_cmd = "pip3 install -r requirements.txt"
    
    if not run_command(pip_cmd, "Installing dependencies"):
        print("⚠️  Failed to install dependencies. Please run manually:")
        print(f"   {pip_cmd}")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Step 2: Run orchestration pipeline
    print_header("STEP 2: Running Complete Pipeline (Database → ML → Alerts → Ready)")
    
    if platform.system() == "Windows":
        pipeline_cmd = "python orchestrate.py"
    else:
        pipeline_cmd = "python3 orchestrate.py"
    
    if not run_command(pipeline_cmd, "Executing orchestration pipeline"):
        print("❌ Pipeline execution failed.")
        print("Review the error messages above and check database_setup.py, ml_pipeline.py, and sql_action_engine.py")
        sys.exit(1)
    
    # Step 3: Final instructions
    print_header("✅ PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    
    print("""
📊 NEXT STEP: Launch the Interactive Dashboard

Run the following command in your terminal:

""")
    
    if platform.system() == "Windows":
        print("   streamlit run app.py")
    else:
        print("   streamlit run app.py")
    
    print("""
The dashboard will open in your browser at:
   http://localhost:8501

📋 Features Available in Dashboard:
   ✓ Real-time KPI metrics
   ✓ 7-day forecast vs historical sales charts
   ✓ Color-coded inventory alerts (Critical/Watchlist/Healthy)
   ✓ Interactive product analysis
   ✓ Alert distribution by category
   ✓ CSV export functionality

🎯 What to Review:
   1. Check "Critical Restock" items - these need immediate action
   2. Monitor "Watchlist" products - reorder soon
   3. Compare predicted demand vs historical sales in charts
   4. Export daily reports for operations team

📁 Project Files:
   • orchestrate.py          → Run complete pipeline
   • database_setup.py       → Database initialization
   • ml_pipeline.py          → ML model training
   • sql_action_engine.py    → Reorder alerts
   • app.py                  → Streamlit dashboard
   • README.md               → Full documentation

🔄 Daily Operation:
   1. Run: python orchestrate.py  (generates fresh forecasts)
   2. Run: streamlit run app.py    (view updated dashboard)

✨ System is ready for production use!
""")
    
    # Offer to launch dashboard
    print("\n" + "-" * 80)
    response = input("Would you like to launch the dashboard now? (y/n): ").strip().lower()
    
    if response == 'y':
        print("\n🚀 Launching Streamlit dashboard...\n")
        if platform.system() == "Windows":
            os.system("streamlit run app.py")
        else:
            os.system("streamlit run app.py")
    else:
        print("\n✅ Setup complete! Run 'streamlit run app.py' when ready to view the dashboard.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

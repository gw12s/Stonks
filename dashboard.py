"""
STONKS Dashboard Launcher 🚀

Clean, simple entry point for the dashboard.
All the heavy lifting happens in the dashboard/ module.

This keeps the root directory clean and professional.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Launch the Streamlit dashboard."""
    try:
        from dashboard.main import run_dashboard
        run_dashboard()
    except ImportError as e:
        print(f"❌ Dashboard module not found: {e}")
        print("Make sure to create the dashboard/ directory and components")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to launch dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
import os
import sys

# Get root project path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

# Add scripts directory to sys.path
sys.path.append(os.path.join(PROJECT_ROOT, "scripts"))

try:
    from chunking_pipeline import run_chunking_pipeline
    run_chunking_pipeline()
except Exception as e:
    print(f"Error running pipeline: {e}")

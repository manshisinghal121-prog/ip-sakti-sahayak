import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

backend_main = os.path.join(PROJECT_ROOT, "backend", "main.py")
print(f"Launching API Server from {backend_main}...")
os.system(f"python \"{backend_main}\"")

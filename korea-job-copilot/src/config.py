"""Central config loaded from environment variables (.env)."""
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = os.getenv("COPILOT_MODEL", "claude-sonnet-4-6")
MY_TOPIK_LEVEL = os.getenv("MY_TOPIK_LEVEL", "TOPIK 2")

RESUME_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "resume")
APPLICATIONS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "applications")
LOG_PATH = os.path.join(APPLICATIONS_DIR, "log.csv")

if not ANTHROPIC_API_KEY:
    # Not raising here so tests / --help can still run without a key.
    pass

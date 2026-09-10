"""
Simon AI - Local AI Assistant inspired by JARVIS (all-free stack)
"""

import sys
import warnings

# Ensure UTF-8 output on Windows terminal
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Suppress known harmless third-party deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="speech_recognition.*")
warnings.filterwarnings("ignore", message=".*aifc was removed in Python 3.13.*")

__version__ = "0.2.0"


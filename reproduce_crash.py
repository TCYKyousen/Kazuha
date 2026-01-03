import sys
import os
import traceback
from crash_handler import CrashHandler, CrashAwareApplication

# Setup crash handler
handler = CrashHandler()
handler.install()

app = CrashAwareApplication(sys.argv, handler)
app.setQuitOnLastWindowClosed(False)

print("Triggering crash directly...")

def crash():
    print("Crashing now!")
    raise RuntimeError("This is a test crash for reproduction.")

try:
    crash()
except Exception:
    exc_type, exc, tb = sys.exc_info()
    handler.handle(exc_type, exc, tb)

print("Main script finished (should not be reached if handle blocks and exits)")

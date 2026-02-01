"""Quick verification script to check all components are properly structured."""
import sys
from pathlib import Path

def check_component(name, module_name):
    """Check if a component can be imported."""
    try:
        __import__(module_name)
        print(f"✓ {name}: OK")
        return True
    except Exception as e:
        print(f"✗ {name}: FAILED - {e}")
        return False

def main():
    """Run verification checks."""
    print("=" * 60)
    print("AI CALL SERVICE - COMPONENT VERIFICATION")
    print("=" * 60)
    print()
    
    components = [
        ("Configuration", "config"),
        ("SIP Integration", "sip_integration"),
        ("Media Handler", "media_handler"),
        ("STT Service", "stt_service"),
        ("Decision Engine", "decision_engine"),
        ("Action Router", "action_router"),
        ("Main Service", "main"),
        ("API Server", "api"),
    ]
    
    results = []
    for name, module in components:
        results.append(check_component(name, module))
    
    print()
    print("=" * 60)
    
    if all(results):
        print("✓ ALL COMPONENTS VERIFIED SUCCESSFULLY")
        print("=" * 60)
        print()
        print("Architecture Flow:")
        print("  Caller (SIP/WebRTC)")
        print("          ↓")
        print("  SIP Server (Asterisk) - sip_integration.py")
        print("          ↓")
        print("  Media (RTP) - media_handler.py")
        print("          ↓")
        print("  STT (Whisper) - stt_service.py")
        print("          ↓")
        print("  Ollama (Decision Engine) - decision_engine.py")
        print("          ↓")
        print("  Action Router - action_router.py")
        print("  ├── Forward (SIP)")
        print("  ├── Voicemail (Record)")
        print("  └── Ask Question (TTS)")
        print()
        return 0
    else:
        print("✗ SOME COMPONENTS FAILED VERIFICATION")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())

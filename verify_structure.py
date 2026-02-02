"""Verification script that checks code structure without importing."""
import ast
from pathlib import Path

def analyze_python_file(filepath):
    """Analyze a Python file and extract key information."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and not node.name.startswith('_')]
        
        return {
            'classes': classes,
            'functions': functions,
            'valid': True
        }
    except SyntaxError as e:
        return {
            'valid': False,
            'error': str(e)
        }

def main():
    """Run code structure verification."""
    print("=" * 70)
    print("AI CALL SERVICE - CODE STRUCTURE VERIFICATION")
    print("=" * 70)
    print()
    
    components = {
        'config.py': {
            'description': 'Configuration Management',
            'expected_classes': ['Settings']
        },
        'sip_integration.py': {
            'description': 'SIP/Asterisk Integration',
            'expected_classes': ['SIPIntegration']
        },
        'media_handler.py': {
            'description': 'Media (RTP) Handling',
            'expected_classes': ['MediaHandler']
        },
        'stt_service.py': {
            'description': 'STT (Whisper) Service',
            'expected_classes': ['STTService']
        },
        'decision_engine.py': {
            'description': 'Ollama Decision Engine',
            'expected_classes': ['DecisionEngine']
        },
        'action_router.py': {
            'description': 'Action Router',
            'expected_classes': ['ActionRouter']
        },
        'main.py': {
            'description': 'Main AI Service Orchestrator',
            'expected_classes': ['AICallService']
        },
        'api.py': {
            'description': 'Aiohttp Web Server',
            'expected_classes': ['CallRequest', 'CallResponse']
        }
    }
    
    all_valid = True
    
    for filename, info in components.items():
        filepath = Path(filename)
        if not filepath.exists():
            print(f"✗ {filename}: FILE NOT FOUND")
            all_valid = False
            continue
        
        analysis = analyze_python_file(filepath)
        
        if not analysis['valid']:
            print(f"✗ {filename}: SYNTAX ERROR - {analysis['error']}")
            all_valid = False
            continue
        
        # Check for expected classes
        missing_classes = [cls for cls in info['expected_classes'] if cls not in analysis['classes']]
        
        if missing_classes:
            print(f"✗ {filename}: Missing classes {missing_classes}")
            all_valid = False
        else:
            print(f"✓ {filename}: {info['description']}")
            print(f"  Classes: {', '.join(analysis['classes'])}")
            if analysis['functions']:
                print(f"  Functions: {', '.join(analysis['functions'][:5])}{'...' if len(analysis['functions']) > 5 else ''}")
    
    print()
    print("=" * 70)
    
    if all_valid:
        print("✓ ALL COMPONENTS HAVE VALID STRUCTURE")
        print("=" * 70)
        print()
        print("ARCHITECTURE IMPLEMENTATION:")
        print()
        print("  1. Caller (SIP/WebRTC)")
        print("          ↓")
        print("  2. SIP Server (Asterisk) -------- sip_integration.py [SIPIntegration]")
        print("          ↓")
        print("  3. Media (RTP) ------------------ media_handler.py [MediaHandler]")
        print("          ↓")
        print("  4. STT (Whisper) ---------------- stt_service.py [STTService]")
        print("          ↓")
        print("  5. Ollama (Decision Engine) ----- decision_engine.py [DecisionEngine]")
        print("          ↓")
        print("  6. Action Router ---------------- action_router.py [ActionRouter]")
        print("     ├── Forward (SIP) ------------ forward_call()")
        print("     ├── Voicemail (Record) ------- record_voicemail()")
        print("     └── Ask Question (TTS) ------- ask_question()")
        print()
        print("ORCHESTRATION:")
        print("  • Main Service: main.py [AICallService]")
        print("  • REST API: api.py [Aiohttp endpoints]")
        print()
        print("CONFIGURATION:")
        print("  • Settings: config.py [Settings]")
        print("  • Environment: .env.example")
        print()
        return 0
    else:
        print("✗ SOME COMPONENTS HAVE STRUCTURAL ISSUES")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

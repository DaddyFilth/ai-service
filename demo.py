"""Example usage and demonstration of the AI Call Service."""
import asyncio
import logging
from pathlib import Path
import json

from main import AICallService

# Configure logging for demo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_call_flow():
    """Demonstrate the complete call flow."""
    logger.info("=" * 60)
    logger.info("AI CALL SERVICE DEMONSTRATION")
    logger.info("=" * 60)
    
    # Initialize service
    service = AICallService()
    await service.start()
    
    # Example scenarios
    scenarios = [
        {
            "name": "Sales Inquiry",
            "call_data": {
                "call_id": "demo_001",
                "caller_number": "+1-555-0001",
                "called_number": "+1-555-MAIN",
                "timestamp": "2026-02-01T14:19:20Z",
                "channel": "SIP/demo-00000001"
            },
            "description": "Caller wants to speak with sales department"
        },
        {
            "name": "Leave Message",
            "call_data": {
                "call_id": "demo_002",
                "caller_number": "+1-555-0002",
                "called_number": "+1-555-MAIN",
                "timestamp": "2026-02-01T14:20:00Z",
                "channel": "SIP/demo-00000002"
            },
            "description": "Caller wants to leave a voicemail"
        },
        {
            "name": "General Inquiry",
            "call_data": {
                "call_id": "demo_003",
                "caller_number": "+1-555-0003",
                "called_number": "+1-555-MAIN",
                "timestamp": "2026-02-01T14:21:00Z",
                "channel": "SIP/demo-00000003"
            },
            "description": "Caller needs more information"
        }
    ]
    
    # Process each scenario
    for i, scenario in enumerate(scenarios, 1):
        logger.info("")
        logger.info(f"Scenario {i}: {scenario['name']}")
        logger.info(f"Description: {scenario['description']}")
        logger.info("-" * 60)
        
        try:
            result = await service.handle_call(scenario["call_data"])
            logger.info(f"Result: {json.dumps(result, indent=2)}")
        except Exception as e:
            logger.error(f"Error in scenario {i}: {e}")
        
        # Wait between scenarios
        await asyncio.sleep(1)
    
    await service.stop()
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("DEMONSTRATION COMPLETE")
    logger.info("=" * 60)


async def demo_individual_components():
    """Demonstrate individual components."""
    logger.info("\n=== Testing Individual Components ===\n")
    
    # Test SIP Integration
    from sip_integration import SIPIntegration
    logger.info("1. SIP Integration")
    sip = SIPIntegration()
    await sip.connect()
    call_context = await sip.handle_incoming_call({
        "call_id": "comp_test_1",
        "caller_number": "+1234567890",
        "called_number": "+0987654321"
    })
    logger.info(f"   Call context: {call_context}")
    
    # Test Media Handler
    from media_handler import MediaHandler
    logger.info("\n2. Media Handler")
    media = MediaHandler()
    await media.stream_tts("comp_test_1", "This is a test message")
    logger.info("   TTS streaming completed")
    
    # Test Decision Engine
    from decision_engine import DecisionEngine
    logger.info("\n3. Decision Engine")
    engine = DecisionEngine()
    decision = engine._parse_decision("I need to speak with sales", "original")
    logger.info(f"   Decision: {decision}")
    
    # Test Action Router
    from action_router import ActionRouter
    logger.info("\n4. Action Router")
    router = ActionRouter()
    result = await router.ask_question(
        {"call_id": "comp_test_1"},
        {"question": "How can I help you?"}
    )
    logger.info(f"   Action result: {result}")


async def main():
    """Main demo entry point."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--components":
        await demo_individual_components()
    else:
        await demo_call_flow()


if __name__ == "__main__":
    asyncio.run(main())

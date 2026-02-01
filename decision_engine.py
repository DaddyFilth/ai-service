"""Decision engine using Ollama for AI-powered call routing."""
import ollama
from typing import Dict, Any, Optional
import logging
from config import settings

logger = logging.getLogger(__name__)


class DecisionEngine:
    """AI decision engine using Ollama."""
    
    def __init__(self, host: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the decision engine.
        
        Args:
            host: Ollama server host (defaults to settings)
            model: Model to use (defaults to settings)
        """
        self.host = host or settings.ollama_host
        self.model = model or settings.ollama_model
        self.client = ollama.Client(host=self.host)
        logger.info(f"Decision engine initialized with host: {self.host}, model: {self.model}")
    
    def analyze_call(self, transcribed_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze transcribed call content and decide on action.
        
        Args:
            transcribed_text: Text from speech-to-text
            context: Additional context about the call
            
        Returns:
            Dictionary with decision and parameters
        """
        logger.info(f"Analyzing call with text: {transcribed_text}")
        
        # Build the prompt for the AI
        prompt = self._build_prompt(transcribed_text, context)
        
        try:
            # Get decision from Ollama
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI call routing assistant. Analyze incoming calls and decide the best action: 'forward' to route the call, 'voicemail' to record a message, or 'ask_question' to gather more information. Respond with JSON format: {\"action\": \"forward|voicemail|ask_question\", \"reason\": \"explanation\", \"parameters\": {}}."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            decision_text = response['message']['content']
            logger.info(f"Decision from Ollama: {decision_text}")
            
            # Parse the decision
            decision = self._parse_decision(decision_text, transcribed_text)
            return decision
            
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            # Default to asking a question if AI fails
            return {
                "action": "ask_question",
                "reason": "AI service unavailable, gathering more information",
                "parameters": {
                    "question": "I'm sorry, could you please repeat your request?"
                }
            }
    
    def _build_prompt(self, transcribed_text: str, context: Optional[Dict[str, Any]]) -> str:
        """Build the prompt for the AI model."""
        prompt = f"Incoming call transcription: '{transcribed_text}'"
        
        if context:
            prompt += f"\n\nContext: {context}"
        
        prompt += "\n\nWhat action should be taken with this call?"
        return prompt
    
    def _parse_decision(self, decision_text: str, original_text: str) -> Dict[str, Any]:
        """
        Parse the AI decision text into a structured format.
        
        Args:
            decision_text: Response from AI
            original_text: Original transcribed text
            
        Returns:
            Structured decision dictionary
        """
        # Try to parse JSON response
        import json
        try:
            decision = json.loads(decision_text)
            if "action" in decision:
                return decision
        except json.JSONDecodeError:
            pass
        
        # Fallback: simple text parsing
        decision_lower = decision_text.lower()
        
        if "forward" in decision_lower or "transfer" in decision_lower:
            return {
                "action": "forward",
                "reason": "Call should be forwarded based on content",
                "parameters": {}
            }
        elif "voicemail" in decision_lower or "record" in decision_lower or "message" in decision_lower:
            return {
                "action": "voicemail",
                "reason": "Caller should leave a voicemail",
                "parameters": {}
            }
        else:
            return {
                "action": "ask_question",
                "reason": "Need more information from caller",
                "parameters": {
                    "question": "How can I help you today?"
                }
            }

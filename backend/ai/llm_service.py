"""
LLM service for generating nutrition explanations and chat responses.

This module provides a unified interface for LLM services including OpenAI
and Hugging Face, with safety-first prompt templates and fallback mechanisms.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMService:
    """Unified LLM service with multiple backend support."""
    
    def __init__(self, openai_api_key: str = None, hf_api_token: str = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.hf_api_token = hf_api_token or os.getenv("HF_API_TOKEN")
        
        # Initialize backends
        self.openai_client = None
        self.hf_pipeline = None
        
        self._initialize_backends()
    
    def _initialize_backends(self):
        """Initialize available LLM backends."""
        # Initialize OpenAI
        if self.openai_api_key:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
        
        # Initialize Hugging Face (fallback)
        if self.hf_api_token:
            try:
                from transformers import pipeline
                self.hf_pipeline = pipeline(
                    "text-generation",
                    model="microsoft/DialoGPT-medium",
                    token=self.hf_api_token
                )
                logger.info("Hugging Face pipeline initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Hugging Face: {e}")
    
    def _get_system_prompt(self) -> str:
        """Get the safety-first system prompt."""
        return """You are a nutrition assistant. Use ONLY the EVIDENCE provided below. If the evidence is insufficient, respond "No verified evidence — suggest safe alternatives" and do not hallucinate. Always include inline citations like [1],[2] after claims. Always provide numeric macros (calories, protein, carbs, fat) and a confidence score. Never provide medical advice; include a standard disclaimer and recommend consulting a qualified professional."""
    
    def _format_evidence(self, facts: List[Dict]) -> str:
        """Format retrieved facts as evidence for the prompt."""
        if not facts:
            return "No evidence available."
        
        evidence_lines = []
        for i, fact in enumerate(facts, 1):
            evidence_lines.append(f"[{i}] {fact['fact_text']}")
        
        return "\n".join(evidence_lines)
    
    def _format_user_profile(self, user_profile: Dict) -> str:
        """Format user profile for the prompt."""
        return f"""Age: {user_profile.get('age', 'Unknown')}, 
Sex: {user_profile.get('gender', 'Unknown')}, 
Weight: {user_profile.get('weight_kg', 'Unknown')} kg, 
Height: {user_profile.get('height_cm', 'Unknown')} cm, 
Activity Level: {user_profile.get('activity_level', 'Unknown')}, 
Goals: {user_profile.get('goal', 'Unknown')}"""
    
    def generate_explanation(self, user_profile: Dict, rf_result: Dict, 
                           retrieved_facts: List[Dict], extra_context: str = "") -> str:
        """
        Generate explanation for food recommendation.
        
        Args:
            user_profile: User profile information
            rf_result: Random Forest prediction result
            retrieved_facts: Retrieved nutrition facts
            extra_context: Additional context
            
        Returns:
            Generated explanation text
        """
        try:
            # Use OpenAI if available
            if self.openai_client:
                return self._generate_with_openai(user_profile, rf_result, retrieved_facts, extra_context)
            
            # Fallback to template-based explanation
            return self._generate_template_explanation(user_profile, rf_result, retrieved_facts, extra_context)
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return self._generate_template_explanation(user_profile, rf_result, retrieved_facts, extra_context)
    
    def _generate_with_openai(self, user_profile: Dict, rf_result: Dict, 
                            retrieved_facts: List[Dict], extra_context: str) -> str:
        """Generate explanation using OpenAI API."""
        evidence = self._format_evidence(retrieved_facts)
        user_profile_str = self._format_user_profile(user_profile)
        
        prompt = f"""EVIDENCE: 
{evidence}

USER_PROFILE: {user_profile_str}

RF_PREDICTION: {'Recommended' if rf_result.get('recommended', False) else 'Not Recommended'} (Confidence: {rf_result.get('confidence', 0):.1%})

INSTRUCTIONS: Propose a meal/portion or say "No verified evidence", show the calculation used to compute totals using the retrieved facts, and list sources at the end.

{extra_context}"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,  # Deterministic for factual answers
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._generate_template_explanation(user_profile, rf_result, retrieved_facts, extra_context)
    
    def chat_message(self, user_profile: Dict, message: str, history: List[Dict] = None, recent_logs: Optional[List] = None) -> str:
        """
        Generate chat response.
        
        Args:
            user_profile: User profile information
            message: User message
            history: Conversation history
            recent_logs: Recent meal logs
            
        Returns:
            Generated response
        """
        try:
            # Use OpenAI if available
            if self.openai_client:
                return self._chat_with_openai(user_profile, message, history, recent_logs=recent_logs)
            
            # Fallback to template response
            return self._generate_template_chat_response(user_profile, message, recent_logs=recent_logs)
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return self._generate_template_chat_response(user_profile, message, recent_logs=recent_logs)
    
    def _chat_with_openai(self, user_profile: Dict, message: str, history: List[Dict] = None, recent_logs: Optional[List] = None) -> str:
        """Generate chat response using OpenAI API."""
        user_profile_str = self._format_user_profile(user_profile)
        
        messages = [
            {"role": "system", "content": self._get_system_prompt() + f"\n\nUSER_PROFILE: {user_profile_str}"}
        ]
        
        # Add conversation history
        if history:
            for h in history[-5:]:  # Last 5 messages
                messages.append({"role": "user", "content": h.get("user", "")})
                messages.append({"role": "assistant", "content": h.get("assistant", "")})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,  # More creative for chat
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            return self._generate_template_chat_response(user_profile, message)
    
    def _generate_template_explanation(self, user_profile: Dict, rf_result: Dict, 
                                     retrieved_facts: List[Dict], extra_context: str) -> str:
        """Generate template-based explanation as fallback."""
        recommended = rf_result.get('recommended', False)
        confidence = rf_result.get('confidence', 0)
        
        # Base explanation
        if recommended:
            base = f"Based on the nutritional analysis, this food is recommended (confidence: {confidence:.1%}). "
        else:
            base = f"Based on the nutritional analysis, this food is not recommended (confidence: {confidence:.1%}). "
        
        # Add evidence-based information
        if retrieved_facts:
            fact = retrieved_facts[0]  # Use the most relevant fact
            base += f"The nutritional profile shows {fact['calories_100g']:.0f} calories, "
            base += f"{fact['protein_100g']:.1f}g protein, {fact['carbs_100g']:.1f}g carbs, "
            base += f"and {fact['fat_100g']:.1f}g fat per 100g. "
        
        # Add user-specific advice
        user_goal = user_profile.get('goal', '').lower()
        if 'weight loss' in user_goal:
            base += "For weight loss goals, consider portion control and overall calorie balance. "
        elif 'muscle' in user_goal or 'strength' in user_goal:
            base += "For muscle building goals, this food's protein content is important. "
        
        # Add disclaimer
        base += "\n\nDisclaimer: This is general nutritional information. Please consult a qualified healthcare professional for personalized dietary advice."
        
        return base
    
    def _generate_template_chat_response(self, user_profile: Dict, message: str, recent_logs: Optional[List] = None) -> str:
        """Generate template-based chat response as fallback, using recent meal logs for context."""
        profile_str = f"age: {user_profile.age}, goal: {user_profile.goal}"
        logs_str = ""
        if recent_logs:
            logs_str = "Here are your recent meals:\n"
            for log in recent_logs:
                food = getattr(log, 'food', None)
                if food:
                    logs_str += f"- {log.date}: {food.name} ({food.calories} kcal, {food.protein}g protein, {food.carbs}g carbs, {food.fats}g fat)\n"
                else:
                    logs_str += f"- {log.date}: Food ID {log.food_id} (details unavailable)\n"
        else:
            logs_str = "No recent meal logs found.\n"
        return f"I understand you're asking about nutrition. Based on your profile ({profile_str}), I'd recommend focusing on a balanced diet with adequate protein, healthy carbs, and good fats.\n\n{logs_str}\nFor more specific advice, please provide more details about your question or consult with a qualified nutritionist.\n\nDisclaimer: This is general information. Please consult a healthcare professional for personalized advice."
    
    def is_available(self) -> bool:
        """Check if any LLM backend is available."""
        return self.openai_client is not None or self.hf_pipeline is not None
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about available backends."""
        return {
            "openai_available": self.openai_client is not None,
            "huggingface_available": self.hf_pipeline is not None,
            "any_available": self.is_available()
        }


# Global LLM service instance
_llm_instance = None

def get_llm_service() -> LLMService:
    """Get the global LLM service instance."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMService()
    return _llm_instance

def generate_explanation(user_profile: Dict, rf_result: Dict, 
                        retrieved_facts: List[Dict], extra_context: str = "") -> str:
    """Convenience function to generate explanation."""
    llm = get_llm_service()
    return llm.generate_explanation(user_profile, rf_result, retrieved_facts, extra_context)

def chat_message(user_profile: Dict, message: str, history: List[Dict] = None, recent_logs: Optional[List] = None) -> str:
    """Convenience function for chat."""
    llm = get_llm_service()
    return llm.chat_message(user_profile, message, history)


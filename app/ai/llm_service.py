"""LLM service for generating explanations and chat responses."""

import os
from openai import OpenAI

class LLMService:
    """Service for interacting with LLMs."""

    def __init__(self, openai_api_key=None):
        """Initialize the service."""
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self._initialize_backends()

    def _initialize_backends(self):
        """Initialize LLM backends."""
        try:
            if self.api_key:
                self.openai_client = OpenAI(api_key=self.api_key)
            else:
                raise ValueError("OpenAI API key not provided")
            self._available = True
        except Exception as e:
            print(f"Error initializing LLM service: {e}")
            self._available = False

    def is_available(self):
        """Check if the service is available."""
        return self._available

    def generate_explanation(self, user_profile, rf_result, retrieved_facts):
        """Generate a personalized explanation."""
        if not self.is_available():
            return "LLM service unavailable"

        try:
            # Construct prompt
            prompt = f"""Given the following information about a user and food item:

User Profile:
- Age: {user_profile.get('age')}
- Gender: {user_profile.get('gender')}
- Weight: {user_profile.get('weight_kg')}kg
- Height: {user_profile.get('height_cm')}cm
- Activity Level: {user_profile.get('activity_level')}
- Goal: {user_profile.get('goal')}

Model Recommendation:
- Recommended: {'Yes' if rf_result['recommended'] else 'No'}
- Confidence: {rf_result['confidence']:.2%}

Nutrition Facts:
"""
            for fact in retrieved_facts:
                prompt += f"- {fact['fact_text']}\n"

            prompt += "\nGenerate a personalized explanation about whether this food aligns with the user's goals."

            response = self.openai_client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "You are a nutrition expert AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=250
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating explanation: {e}")
            return "Error generating explanation"

    def chat_message(self, message, context=None):
        """Generate a chat response."""
        if not self.is_available():
            return "LLM service unavailable"

        try:
            messages = [
                {"role": "system", "content": "You are a nutrition expert AI assistant."},
            ]

            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})

            messages.append({"role": "user", "content": message})

            response = self.openai_client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages,
                temperature=0.7,
                max_tokens=250
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in chat: {e}")
            return "Error processing your message"
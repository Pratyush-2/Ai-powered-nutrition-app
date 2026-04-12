import requests
import json
import os
import logging
from sqlalchemy.orm import Session
from app.crud import get_user_profile, get_user_goals, get_logs_by_user
from app.ai.retriever import retrieve_facts
from datetime import date
from sqlalchemy import func
from app import models

logger = logging.getLogger(__name__)

# Groq API configuration (replaces local Ollama)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

def query_groq(prompt: str) -> str:
    """Query Groq cloud LLM API (replaces local Ollama)."""
    
    if not GROQ_API_KEY:
        return "AI assistant is not configured. Please set GROQ_API_KEY."
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a friendly and knowledgeable nutrition assistant. Keep responses concise and actionable."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 200,
        "top_p": 0.9
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
        
    except requests.exceptions.ConnectionError:
        return "AI assistant is currently unavailable. Please try again later."
    except requests.exceptions.Timeout:
        return "The response is taking longer than expected. Could you try rephrasing your question?"
    except Exception as e:
        logger.error(f"Groq error: {e}")
        return "I'm having trouble processing your request right now. Please try again."

def get_llm_explanation(classification, rag_output):
    try:
        prompt = f"""Based on the following information, provide a user-friendly explanation.

Classification: {'Recommended' if classification['recommended'] else 'Not Recommended'}
Confidence: {classification['confidence']:.2f}

Relevant Nutrition Information:
{rag_output}

Explain why this food is or is not recommended for the user in a conversational and encouraging tone."""

        response = query_groq(prompt)
        
        if response and len(response.strip()) >= 10:
            return response
        else:
            return fallback_explanation(classification)

    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        return fallback_explanation(classification)

def generate_contextual_chat_response(user_query: str, user_id: int, db: Session):
    """Generate contextual chat response using user's nutritional data."""
    
    try:
        # Get user data
        user_profile = get_user_profile(db, user_id)
        user_goals = get_user_goals(db, user_id)
        recent_logs = get_logs_by_user(db, user_id, limit=10)
        
        # Build comprehensive context
        context_parts = []
        
        if user_profile:
            context_parts.append(f"""User Profile:
- Name: {user_profile.name or 'Unknown'}
- Age: {user_profile.age or 'Unknown'} years
- Weight: {user_profile.weight_kg or 'Unknown'} kg
- Height: {user_profile.height_cm or 'Unknown'} cm
- Gender: {user_profile.gender or 'Unknown'}
- Activity Level: {user_profile.activity_level or 'Unknown'}
- Main Goal: {user_profile.goal or 'Unknown'}
- Fitness Goal: {user_profile.fitness_goal or 'Unknown'}
- Allergies: {user_profile.allergies or 'None specified'}
- Health Conditions: {user_profile.health_conditions or 'None specified'}""")
        
        if user_goals:
            first_goal = user_goals[0]
            context_parts.append(f"""Current Nutrition Goals:
- Daily Calories: {first_goal.calories_goal or 'Not set'} kcal
- Daily Protein: {first_goal.protein_goal or 'Not set'}g
- Daily Carbs: {first_goal.carbs_goal or 'Not set'}g  
- Daily Fats: {first_goal.fats_goal or 'Not set'}g""")
        
        if recent_logs:
            context_parts.append("Recent Food Log (last 10 entries):")
            for log in recent_logs[:5]:
                if log.food:
                    food_name = log.food.name
                    quantity = log.quantity
                    calories = log.food.calories * quantity
                    protein = log.food.protein * quantity
                    carbs = log.food.carbs * quantity
                    fats = log.food.fats * quantity
                    context_parts.append(f"- {log.date}: {quantity}x {food_name} ({calories:.0f} kcal, {protein:.1f}g protein, {carbs:.1f}g carbs, {fats:.1f}g fats)")
        
        today = date.today().isoformat()
        today_totals = get_daily_totals_by_user(db, user_id, today)
        if today_totals:
            context_parts.append(f"""Today's Intake So Far:
- Calories: {today_totals['calories']:.0f} kcal
- Protein: {today_totals['protein']:.1f}g
- Carbs: {today_totals['carbs']:.1f}g
- Fats: {today_totals['fats']:.1f}g""")
        
        full_context = "\n\n".join(context_parts)
        
        prompt = f"""You are a knowledgeable nutrition assistant. Use the following user information to provide personalized, helpful responses about nutrition, diet, and healthy living.

{full_context}

User Query: {user_query}

Provide a helpful, personalized response that considers the user's profile, goals, and recent eating patterns. Keep responses informative but conversational. Focus on nutrition and health advice.

Response:"""

        response = query_groq(prompt)
        
        if not response or len(response) < 10:
            response = "I'd be happy to help with your nutrition questions! Based on your profile and goals, I can provide personalized advice about healthy eating, meal planning, and reaching your targets."
        
        if not any(keyword in response.lower() for keyword in ['nutrition', 'food', 'eat', 'health', 'diet', 'protein', 'calories', 'exercise', 'weight']):
            response += "\n\nHow can I help you with your nutrition goals today?"
        
        return response
        
    except Exception as e:
        logger.error(f"Contextual chat generation error: {e}")
        return "I'm having trouble accessing your data right now. Could you try asking your question again?"

def chat_with_llm(user_query: str, user_id: int, db: Session):
    """Enhanced chat system with user context for all responses."""
    
    try:
        user_profile = get_user_profile(db, user_id)
        user_goals = get_user_goals(db, user_id)
        
        query_lower = user_query.lower()
        
        nutrition_keywords = {
            'protein': ['protein', 'muscle', 'strength', 'build muscle'],
            'weight loss': ['weight loss', 'lose weight', 'slimming', 'cut weight'],
            'calories': ['calories', 'calorie counting', 'kcal', 'energy intake'],
            'hydration': ['water', 'hydration', 'drink', 'fluid', 'thirsty'],
            'exercise': ['exercise', 'workout', 'fitness', 'gym', 'training', 'cardio']
        }
        
        for topic, keywords in nutrition_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                if topic == 'protein':
                    return """Protein is crucial for muscle maintenance and overall health. Good sources include:

• Lean meats: chicken, turkey, lean beef
• Fish and seafood: salmon, tuna, shrimp
• Eggs and dairy: Greek yogurt, cottage cheese
• Plant-based: beans, lentils, tofu, quinoa
• Nuts and seeds: almonds, chia seeds, hemp seeds

Aim for 1.2-2.0g of protein per kg of body weight daily, distributed across meals."""
                    
                elif topic == 'weight loss':
                    return """For weight loss, focus on creating a sustainable calorie deficit through healthy eating and regular exercise. Key principles:

• Create a 300-500 calorie daily deficit
• Prioritize whole, nutrient-dense foods
• Include protein in every meal to stay full
• Stay hydrated and get adequate sleep
• Combine with regular physical activity
• Track both weight and measurements

Sustainable changes lead to lasting results!"""
                    
                elif topic == 'calories':
                    return """Calorie management is personal and depends on your goals, age, weight, and activity level. General guidelines:

• Sedentary adults: 1,800-2,400 calories/day
• Lightly active: 2,200-2,800 calories/day  
• Moderately active: 2,400-3,000 calories/day
• Very active: 2,800-3,500+ calories/day

Use calorie tracking as a tool, not a strict rule. Focus on nourishing your body!"""
                    
                elif topic == 'hydration':
                    return """Proper hydration is crucial for health and performance:

• Aim for 8-10 glasses (2-3 liters) of water daily
• More if you're active, in hot weather, or ill
• Signs of dehydration: dark urine, dry mouth, fatigue
• Foods with high water content help too: cucumbers, watermelon, oranges
• Limit sugary drinks and excessive caffeine
• Carry a reusable water bottle as a reminder

Your body is about 60% water - keep it flowing!"""
                    
                elif topic == 'exercise':
                    return """Combining nutrition with exercise maximizes results:

• Strength training: 2-3x/week, all major muscle groups
• Cardio: 150 minutes moderate or 75 minutes vigorous weekly
• Eat protein within 2 hours post-workout
• Stay hydrated during exercise
• Include rest days for recovery
• Balance cardio and strength for optimal body composition

Nutrition fuels performance - eat to support your activity level!"""
        
        # For ALL other queries, use contextual LLM response
        return generate_contextual_chat_response(user_query, user_id, db)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        try:
            return generate_contextual_chat_response(user_query, user_id, db)
        except:
            return "I'm here to help with your nutrition questions! Feel free to ask about healthy eating, protein needs, weight management, or any other nutrition topics."

def fallback_explanation(classification):
    if classification['recommended']:
        return "This food seems like a good choice for you based on your profile and goals. It aligns well with your nutritional needs."
    else:
        return "This food might not be the best choice for you right now. It may not align with your current nutritional goals. Consider looking for alternatives."

def get_daily_totals_by_user(db: Session, user_id: int, date: str):
    """Get daily nutrition totals for a specific user and date."""
    totals = (
        db.query(
            func.sum(models.Food.calories * models.DailyLog.quantity).label("calories"),
            func.sum(models.Food.protein * models.DailyLog.quantity).label("protein"),
            func.sum(models.Food.carbs * models.DailyLog.quantity).label("carbs"),
            func.sum(models.Food.fats * models.DailyLog.quantity).label("fats"),
        )
        .join(models.Food, models.DailyLog.food_id == models.Food.id)
        .filter(
            models.DailyLog.user_id == user_id,
            models.DailyLog.date == date
        )
        .first()
    )

    if totals and any(totals):
        return {
            "calories": float(totals[0] or 0),
            "protein": float(totals[1] or 0),
            "carbs": float(totals[2] or 0),
            "fats": float(totals[3] or 0),
        }
    
    return {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}

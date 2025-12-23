import httpx
import asyncio
from sqlalchemy.orm import Session
from app.crud import get_user_profile, get_user_goals, get_logs_by_user
from datetime import date, datetime, timedelta

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3:mini"

PROMPT_TEMPLATE_GENERAL = """
You are a friendly and knowledgeable nutrition assistant. Your goal is to provide clear, helpful, and personalized advice.

Here is some context about the user:
{user_context}

User's Question: "{user_input}"

Please structure your response in the following format, keeping it clear and easy to read:

**Friendly opener (1 line):** Start with a warm and encouraging sentence.

**Direct Answer (2-4 lines):** Provide a straightforward answer to the user's question.

**✅ What’s Good:**
- Bullet point 1
- Bullet point 2
- Bullet point 3

**⚠️ Watch Out:**
- Bullet point 1 (Only if there's a very common or important pitfall)

**💡 Tips / Better Choices:**
- Actionable suggestion 1
- Actionable suggestion 2
- Actionable suggestion 3

**🎯 For You:** Briefly explain how this advice specifically helps the user achieve their personal goals (e.g., "This will help you with your goal of...").

**❓ Quick Follow-up:** Ask one short, engaging question to encourage a continued conversation.
"""

PROMPT_TEMPLATE_FOOD_SPECIFIC = """
You are a friendly and knowledgeable nutrition assistant. A user is asking if a specific food is a good choice for them.

Here is some context about the user:
{user_context}

User's Question: "{user_input}"

Please provide a small, direct explanation (3-5 sentences) answering their question. Consider the user's goals and health profile when deciding if the food is a good choice. Explain your reasoning clearly and concisely. Start with a friendly opener.
"""

async def build_user_context(db: Session, user_id: int) -> str:
    """Build comprehensive user context including detailed food logs."""
    return await asyncio.to_thread(_build_user_context_sync, db, user_id)

def _build_user_context_sync(db: Session, user_id: int) -> str:
    """Synchronous version of building user context."""
    
    context_parts = []
    
    user_profile = get_user_profile(db, user_id)
    if user_profile:
        context_parts.append(f"""USER PROFILE:
- Name: {user_profile.name or 'Not specified'}
- Age: {user_profile.age or 'Not specified'}
- Gender: {user_profile.gender or 'Not specified'}
- Weight: {user_profile.weight_kg or 'Not specified'} kg
- Height: {user_profile.height_cm or 'Not specified'} cm
- Activity Level: {user_profile.activity_level or 'Not specified'}
- Main Goal: {user_profile.goal or 'Not specified'}
- Fitness Goal: {user_profile.fitness_goal or 'Not specified'}
- Allergies: {user_profile.allergies or 'None'}
- Health Conditions: {user_profile.health_conditions or 'None'}""")
    
    user_goals = get_user_goals(db, user_id)
    if user_goals:
        goal = user_goals[0]
        context_parts.append(f"""CURRENT NUTRITION GOALS:
- Daily Calories: {goal.calories_goal or 'Not set'} kcal
- Daily Protein: {goal.protein_goal or 'Not set'}g
- Daily Carbs: {goal.carbs_goal or 'Not set'}g
- Daily Fats: {goal.fats_goal or 'Not set'}g""")
    
    seven_days_ago = datetime.now().date() - timedelta(days=7)
    recent_logs = get_logs_by_user(db, user_id, limit=20)
    if recent_logs:
        context_parts.append("RECENT FOOD LOGS (Last 7 days):")
        recent_entries = []
        for log in recent_logs:
            if log.food and log.date >= seven_days_ago:
                food_name = log.food.name
                quantity = log.quantity
                calories = log.food.calories * quantity if log.food.calories else 0
                protein = log.food.protein * quantity if log.food.protein else 0
                carbs = log.food.carbs * quantity if log.food.carbs else 0
                fats = log.food.fats * quantity if log.food.fats else 0
                
                entry = f"- {log.date}: {quantity}x {food_name} ({calories:.0f} kcal, {protein:.1f}g P, {carbs:.1f}g C, {fats:.1f}g F)"
                recent_entries.append(entry)
        
        if recent_entries:
            context_parts.append("\n".join(recent_entries[:10]))
        else:
            context_parts.append("- No recent logs in the last 7 days")
    
    return "\n\n".join(context_parts)

async def query_ollama(prompt: str) -> str:
    """Asynchronously query Ollama with optimized settings."""
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "num_predict": 450, 
            "num_ctx": 3000,
            "repeat_penalty": 1.1,
            "repeat_last_n": 64
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(OLLAMA_URL, json=payload, timeout=30.0)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
            
        except httpx.ConnectError:
            return "AI assistant is currently unavailable. Please try again later."
        except httpx.TimeoutException:
            return "The response is taking longer than expected. Could you try rephrasing your question?"
        except Exception as e:
            print(f"Ollama error: {e}")
            return "I'm having trouble processing your request right now. Please try again."

def is_greeting_only(text: str) -> bool:
    """Check if input is just a greeting with no real question."""
    greetings = {
        "hi", "hello", "hey", "sup", "yo", "hiya", "greetings", "good morning", 
        "good afternoon", "good evening", "howdy", "aloha", "bonjour", "hola",
        "hi there", "hey there", "hello there", "what's up", "whats up", "wassup"
    }
    text_clean = text.lower().strip()
    if text_clean in greetings:
        return True
    if len(text_clean.split()) <= 2 and any(greet in text_clean for greet in ["hi", "hey", "hello", "sup"]):
        return True
    return False

def is_food_specific_question(text: str) -> bool:
    """Check if the question is about a specific food."""
    text_lower = text.lower()
    return "is" in text_lower and "a good choice for me" in text_lower

async def chat_with_ai(db: Session, user_id: int, user_input: str) -> str:
    """Asynchronous and enhanced chat function with detailed context and prompt engineering."""
    
    user_input_clean = user_input.lower().strip()
    
    if await asyncio.to_thread(is_greeting_only, user_input):
        user_profile = await asyncio.to_thread(get_user_profile, db, user_id)
        user_name = user_profile.name if user_profile else "there"
        return f"Hello {user_name}! I'm your nutrition assistant. How can I help you with your health and wellness goals today?"

    try:
        user_context = await build_user_context(db, user_id)
        
        if is_food_specific_question(user_input):
            prompt = PROMPT_TEMPLATE_FOOD_SPECIFIC.format(user_context=user_context, user_input=user_input)
        else:
            prompt = PROMPT_TEMPLATE_GENERAL.format(user_context=user_context, user_input=user_input)

        response = await query_ollama(prompt)
        
        if response and len(response.strip()) >= 20:
            return response
        
        return "I'm not quite sure how to respond to that. Could you try asking me a different question about your nutrition?"
        
    except Exception as e:
        print(f"Chat error: {e}")
        return "I'm having some technical difficulties right now. Could you try asking your question again in a moment?"

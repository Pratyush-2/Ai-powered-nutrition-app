
import openai
import os

# It's recommended to set the API key in your environment variables
# openai.api_key = os.getenv("OPENAI_API_KEY")


def get_llm_explanation(classification, rag_output):
    try:
        prompt = f"""Based on the following information, provide a user-friendly explanation.

Classification: {'Recommended' if classification['recommended'] else 'Not Recommended'}
Confidence: {classification['confidence']:.2f}

Relevant Nutrition Information:
{rag_output}

Explain why this food is or is not recommended for the user in a conversational and encouraging tone."""

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"LLM generation failed: {e}")
        return fallback_explanation(classification)

def chat_with_llm(user_query, user_history):
    try:
        messages = user_history + [{"role": "user", "content": user_query}]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"LLM chat failed: {e}")
        return "I'm sorry, I'm having trouble connecting to my brain right now. Please try again later."

def fallback_explanation(classification):
    if classification['recommended']:
        return "This food seems like a good choice for you based on your profile and goals. It aligns well with your nutritional needs."
    else:
        return "This food might not be the best choice for you right now. It may not align with your current nutritional goals. Consider looking for alternatives."

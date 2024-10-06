from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the API key from environment variable
api_key = os.getenv("api_key")  # Changed to match your .env file

if not api_key:
    raise ValueError("api_key environment variable not set")  # Updated error message

llm = ChatGroq(
    temperature=0.7, groq_api_key=api_key, model_name="llama-3.1-70b-versatile"
)


def generate_recipe(ingredients, button_state):
    prompt = f"Create a recipe using the following ingredients: {', '.join(ingredients)}. Provide the title, ingredients list, and step-by-step instructions. Also, rate the tastiness of the recipe on a scale of 1-10."

    response = llm.invoke(prompt)
    return response.content

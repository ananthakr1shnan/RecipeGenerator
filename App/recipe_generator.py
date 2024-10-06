import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from environment variables
api_key = os.getenv("api_key")

if not api_key:
    raise ValueError("GROQ API key not found. Please check your .env file.")

# Initialize ChatGroq
llm = ChatGroq(temperature=0.7, groq_api_key=api_key, model_name="llama-3.1-70b-versatile")


def generate_recipe(selected_items):
    prompt = f"""Create a recipe using the following ingredients: {', '.join(selected_items)}.
    Please format the recipe as follows:
    
    Recipe Name:
    Ingredients:
    - [List of ingredients with quantities]
    
    Instructions:
    1. [Step 1]
    2. [Step 2]
    ...
    
    Cooking Time: [Estimated cooking time]
    Servings: [Number of servings]
    """

    response = llm.invoke(prompt)
    return response.content

import os
import openai
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# Get the API key from environment variable
api_key = os.getenv("SAMBANOVA_API_KEY")

if not api_key:
    raise ValueError("SAMBANOVA_API_KEY environment variable not set")

# Initialize the OpenAI client with SambaNova configuration
client = openai.OpenAI(
    api_key=api_key,
    base_url="https://api.sambanova.ai/v1",
)


def generate_recipe(ingredients, button_state):
    # List of different prompt styles
    prompt_styles = [
        "Create a unique recipe using these ingredients: {ingredients}. Provide a catchy title, full ingredients list, and detailed instructions. Rate its tastiness from 1-10.",
        "Invent a fusion dish combining cuisines, using these ingredients: {ingredients}. Include a creative name, all ingredients needed, step-by-step guide, and taste rating (1-10).",
        "Design a gourmet meal featuring these ingredients: {ingredients}. Give it an elegant name, list all components, provide a chef's guide to preparation, and rate its flavor profile (1-10).",
        "Craft a quick and easy recipe with these items: {ingredients}. Choose a simple name, list ingredients with amounts, write clear instructions, and score its taste appeal (1-10).",
    ]

    # Randomly select a prompt style
    selected_prompt = random.choice(prompt_styles)

    # Format the prompt with the given ingredients
    prompt = selected_prompt.format(ingredients=", ".join(ingredients))

    if button_state > 4:
        button_state = 4

    # Add some randomness to temperature
    temperature = 0.5 + (button_state / 10) + random.uniform(0, 0.2)

    response = client.chat.completions.create(
        model="Meta-Llama-3.1-8B-Instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        top_p=0.1 + random.uniform(0, 0.1),  # Add some randomness to top_p as well
    )

    return response.choices[0].message.content

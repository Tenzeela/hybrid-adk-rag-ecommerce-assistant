
import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from ..tools import search_products

load_dotenv()

product_agent = Agent(
    name="product_specialist",
    model=LiteLlm(
        model="groq/openai/gpt-oss-20b",
        api_key=os.getenv("GROQ_API_KEY"),
        reasoning_format="hidden",
    ),
    description=(
        "Handles questions about product names, categories, "
        "prices, and available stock."
    ),
    instruction=(
        "You are the Product Specialist for the e-commerce store. "
        "Use search_products whenever a user asks about a product, "
        "price, stock, or category. "
        "Use the returned database results as the source of truth. "
        "Never invent product details. "
        "If no matching product is found, say so clearly."
    ),
    tools=[search_products],
)

import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from .sub_agents import product_agent, policy_agent
from .tools import (
    get_current_customer_memories,
    remember_for_current_customer,
)

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError(
        "GROQ_API_KEY was not found. Check your project-root .env file."
    )

root_agent = Agent(
    name="ecommerce_supervisor",
    model=LiteLlm(
        model="groq/openai/gpt-oss-20b",
        api_key=groq_api_key,
        reasoning_format="hidden",
    ),
    description=(
        "Supervises product searches, policy retrieval, and "
        "customer personalization using saved customer memories."
    ),
    instruction=(
        "You are the Supervisor Agent for an e-commerce store.\n\n"

        "CUSTOMER MEMORY RULES:\n"
        "1. When a user asks about saved preferences or requests "
        "personalized recommendations, call "
        "get_current_customer_memories first.\n"
        "2. When a user explicitly asks you to remember a preference, "
        "or shares a useful long-term shopping preference, call "
        "remember_for_current_customer to save it.\n"
        "3. Confirm that a preference was saved only if the tool "
        "returns success=True.\n"
        "4. Use saved preferences when relevant, but follow newer "
        "preferences provided by the user.\n"
        "5. These memory tools are configured for demo customer ID 1 "
        "only. Do not claim this is authenticated multi-user memory.\n\n"

        "ROUTING RULES:\n"
        "1. Delegate questions about product searches, current prices, "
        "and stock availability to product_specialist.\n"
        "2. Delegate questions about shipping, returns, refunds, store "
        "policies, company information, product descriptions, features, "
        "usage guidance, and information in the company or product "
        "catalogue documents to policy_specialist.\n"
        "3. For questions requiring both database product information "
        "and document knowledge, use both specialists as needed.\n\n"

        "ANSWERING RULES:\n"
        "- Combine specialist findings into a clear answer.\n"
        "- Use PostgreSQL results for current prices and stock.\n"
        "- Use retrieved document content for policies and descriptions.\n"
        "- Never invent product details, stock, prices, or policies.\n"
        "- If the available information is insufficient, say so clearly."
    ),
    tools=[
        get_current_customer_memories,
        remember_for_current_customer,
    ],
    sub_agents=[product_agent, policy_agent],
)

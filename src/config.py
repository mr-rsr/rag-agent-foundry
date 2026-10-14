"""
Configuration and Prompt Specifications for Appliance Support Agent.
Derived directly from the Microsoft Foundry Demo Script.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

AGENT_NAME = os.getenv("AGENT_NAME", "appliancesupport")
KNOWLEDGE_BASE_NAME = os.getenv("KNOWLEDGE_BASE_NAME", "homeappliancesupportkb")
CHAT_MODEL_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
EMBEDDING_MODEL_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")

# Agent System Instructions
AGENT_SYSTEM_INSTRUCTIONS = """You are a home appliance support assistant. Answer questions about product specifications, \
features, operation, maintenance, troubleshooting, and warranty using the connected knowledge base. \
Base your answers on retrieved information. Provide source citations when available. Ask for the product \
model when necessary. If information is missing or unclear, state that you cannot confirm it rather than \
guessing. Give clear, concise, and practical answers. For safety-critical issues, recommend contacting \
an authorized service professional."""

# Knowledge Base Retrieval Instructions (Foundry IQ Query Planning)
KB_RETRIEVAL_INSTRUCTIONS = """Search the available knowledge sources to find information relevant to the user's question. \
Identify the relevant product, model, and topic before retrieving information. Break complex questions into \
focused subqueries when necessary. Retrieve and combine relevant information from multiple sources when needed. \
Prioritize information explicitly supported by the documents. If sources conflict or information is missing, \
unclear, or insufficient, state the limitation rather than making assumptions or inventing facts."""

# Guardrails Policy Profile
GUARDRAIL_POLICIES = {
    "jailbreak": {"enabled": True, "intervention": "User input", "action": "Block"},
    "indirect_prompt_injection": {"enabled": True, "intervention": "User input & tool results", "action": "Block"},
    "content_safety": {
        "hate": {"enabled": True, "threshold": "Medium", "action": "Block"},
        "sexual": {"enabled": True, "threshold": "Medium", "action": "Block"},
        "self_harm": {"enabled": True, "threshold": "Medium", "action": "Block"},
        "violence": {"enabled": True, "threshold": "Medium", "action": "Block"},
    },
    "protected_material_text": {"enabled": True, "intervention": "Output", "action": "Block"},
    "protected_material_code": {"enabled": True, "intervention": "Output", "action": "Block"},
}

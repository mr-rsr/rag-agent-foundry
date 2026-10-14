# Before running the sample:
#    pip install "azure-ai-projects>=2.1.0" azure-identity python-dotenv

import os
import sys
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Load configuration from .env if present
load_dotenv()

endpoint = os.getenv(
    "PROJECT_ENDPOINT",
    "https://rajaryanrsr-2592-resource.services.ai.azure.com/api/projects/rajaryanrsr-2592",
)
agent_name = os.getenv("AGENT_NAME", "appliancesupportagent")
user_message = (
    sys.argv[1]
    if len(sys.argv) > 1
    else "What is the cooling capacity of model AH-SI18V5B-SCN?"
)

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=endpoint,
        credential=credential,
        allow_preview=True,
    ) as project_client,
):
    # Bind the OpenAI client to the existing agent endpoint.
    openai_client = project_client.get_openai_client(agent_name=agent_name)

    # GitHub Copilot preview agents require a conversation for every Responses turn.
    conversation = openai_client.conversations.create()

    # Retry loop to handle transient TPM rate limits gracefully
    import time
    from openai import RateLimitError

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = openai_client.responses.create(
                conversation=conversation.id,
                input=[{"role": "user", "content": user_message}],
            )
            print(f"Response output:\n{response.output_text}")
            break
        except RateLimitError as err:
            if attempt < max_retries - 1:
                print(f"Hit temporary rate limit. Retrying in 15 seconds (attempt {attempt + 1}/{max_retries})...")
                time.sleep(15)
            else:
                raise err

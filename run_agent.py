"""
Access your Azure AI Foundry Agent ('appliancesupport') via code.

Requirements:
    pip install azure-ai-projects azure-identity python-dotenv

Usage:
    python run_agent.py "What is the cooling capacity of model AH-SI18V5B-SCN?"
"""

import os
import sys
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Load configuration from .env file
load_dotenv()

CONNECTION_STRING = os.getenv("PROJECT_CONNECTION_STRING")
AGENT_NAME = os.getenv("AGENT_NAME", "appliancesupport")
AGENT_ID = os.getenv("AGENT_ID")  # Optional: specify exact agent ID from portal


def query_agent(prompt: str):
    if not CONNECTION_STRING:
        print("=" * 60)
        print("Error: Missing PROJECT_CONNECTION_STRING in your environment or .env file.")
        print("To find your connection string:")
        print("1. Go to https://ai.azure.com")
        print("2. Open your Project -> Project Settings -> Overview")
        print("3. Copy 'Project connection string'")
        print("=" * 60)
        return

    print("Authenticating with Azure AI Foundry...")
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=CONNECTION_STRING,
    )

    with project_client:
        # 1. Locate the agent created in Foundry UI
        target_agent = None
        if AGENT_ID:
            target_agent = project_client.agents.get_agent(AGENT_ID)
        else:
            agent_list = project_client.agents.list_agents().data
            for a in agent_list:
                if a.name == AGENT_NAME:
                    target_agent = a
                    break

        if not target_agent:
            print(f"Error: Could not find an agent named '{AGENT_NAME}'.")
            print("Available agents in this project:")
            for a in project_client.agents.list_agents().data:
                print(f"  - {a.name} (ID: {a.id})")
            print("You can set AGENT_ID directly in .env if desired.")
            return

        print(f"Connected to Agent: {target_agent.name} (ID: {target_agent.id})")

        # 2. Create a conversation thread
        thread = project_client.agents.create_thread()

        # 3. Add the user message
        project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=prompt,
        )

        # 4. Run the agent and wait for completion
        print(f"\nAsking: \"{prompt}\"")
        run = project_client.agents.create_and_process_run(
            thread_id=thread.id,
            assistant_id=target_agent.id,
        )

        # 5. Retrieve and print the response
        messages = project_client.agents.list_messages(thread_id=thread.id)
        for msg in messages.data:
            if msg.role == "assistant":
                for item in msg.content:
                    if hasattr(item, "text"):
                        print("\nAgent Response:")
                        print("-" * 60)
                        print(item.text.value)
                        print("-" * 60)
                break


if __name__ == "__main__":
    query = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "What is the cooling capacity of model AH-SI18V5B-SCN?"
    )
    query_agent(query)

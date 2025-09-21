import os
import requests
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
# from azure.ai.projects.models import FunctionTool

# Set env variables (fill with your values)
os.environ["AZURE_CLIENT_ID"] = "e7aed50a-a8fe-45d2-9d59-dcebe5d69d31"
os.environ["AZURE_TENANT_ID"] = "73f84ff0-2b21-4d29-a843-f1edf7043028"
os.environ["AZURE_CLIENT_SECRET"] = "eoD8Q~LX_.oC01be2tK5uy14p~9dtnQFNeviQaJ~"
os.environ["AZUREAI_PROJECT_ENDPOINT"] = "https://sumit0-5029-resource.services.ai.azure.com/api/projects/sumit0-5029"
os.environ["AGENT_ID"] = "asst_J9guwWsc95fMARuWCQ0rDzQB"

# Authenticate (uses az login or environment variables)
credential = DefaultAzureCredential()

# Reference your agent
agent_id = os.environ["AGENT_ID"]

# Initialize project client
project_client = AIProjectClient(
    endpoint=os.environ["AZUREAI_PROJECT_ENDPOINT"],
    credential=credential
)

# Define a simple tool as a dict
wikipedia_tool = {
    "name": "search_wikipedia",
    "description": "Fetches a Wikipedia summary for a given medical term or condition",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Medical term, drug, or condition to search in Wikipedia"
            }
        },
        "required": ["query"]
    },
    "function": lambda query: requests.get(
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
    ).json().get("extract", "No summary found.")
}

# Register tool with the agent
# project_client.agents.create_agent(
#     agent_id=agent_id,
#     tools=[wikipedia_tool]
# )

# Create a conversation thread
thread = project_client.agents.threads.create()

# Add a user message
project_client.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="What is insulin used for?"
)

# Run the agent (agent may call Wikipedia tool)
run = project_client.agents.runs.create_and_process(
    agent_id=agent_id,
    thread_id=thread.id
)

# Get responses
messages = project_client.agents.messages.list(thread_id=thread.id)

print("=== Conversation Trace ===")
for msg in messages:
    print(f"[{msg.role}] {msg.content}")

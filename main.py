import os, time, requests, json
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import FunctionTool
import json
import datetime
from typing import Any, Callable, Set, Dict, List, Optional


# Start by defining a function for your agent to call. 
# When you create a function for an agent to call, you describe its structure 
# with any required parameters in a docstring.

# Set env variables (fill with your values)
os.environ["AZURE_CLIENT_ID"] = "e7aed50a-a8fe-45d2-9d59-dcebe5d69d31"
os.environ["AZURE_TENANT_ID"] = "73f84ff0-2b21-4d29-a843-f1edf7043028"
os.environ["AZURE_CLIENT_SECRET"] = "eoD8Q~LX_.oC01be2tK5uy14p~9dtnQFNeviQaJ~"
# Retrieve the project endpoint from environment variables
project_endpoint = "https://sumit0-5029-resource.services.ai.azure.com/api/projects/sumit0-5029"
model_name = "gpt-4.1"


def search_wikipedia(query: str) -> str:
    """Search Wikipedia for a quick summary of a medical term or topic."""
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        headers = {
            "User-Agent": "MedicalResearchAgent/1.0 (patelsumitsachan0@gmail.com)"
        }
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("extract", "No summary found.")
        else:
            return f"Wikipedia returned status code {resp.status_code}"
    except Exception as e:
        return f"Error fetching from Wikipedia: {str(e)}"

# Define user functions
user_functions = {search_wikipedia}


# Initialize the AIProjectClient
project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential()
)

# Initialize the FunctionTool with user-defined functions
functions = FunctionTool(functions=user_functions)


# Create an agent with custom functions
agent = project_client.agents.create_agent(
    model=model_name,
    name="medical-agent",
    instructions="You have access to a function `search_wikipedia(query)` that contains summaries of medical terms. Always try to call this function first for medical terms. Only use your own knowledge if no result is found.",
    tools=functions.definitions,
)
print(f"Created agent, ID: {agent.id}")

# Create a thread for communication
thread = project_client.agents.threads.create()
print(f"Created thread, ID: {thread.id}")

# Send a message to the thread
message = project_client.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="When was Insulin discovered?",
)
print(f"Created message, ID: {message['id']}")

# Create and process a run for the agent to handle the message
run = project_client.agents.runs.create(thread_id=thread.id, agent_id=agent.id)
print(f"Created run, ID: {run.id}")

# Poll the run status until it is completed or requires action
while run.status in ["queued", "in_progress", "requires_action"]:
    print(f"run Status run: {run.status}")
    time.sleep(1)
    run = project_client.agents.runs.get(thread_id=thread.id, run_id=run.id)

    if run.status == "requires_action":
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
        for tool_call in tool_calls:
            if tool_call.function.name == "search_wikipedia":
                output = search_wikipedia("Insulin")
                if output is None:
                    output = "No summary found."  # fallback
                tool_outputs.append({"tool_call_id": tool_call.id, "output": output})
                print("tool_outputs:", tool_outputs)
        project_client.agents.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs)

print(f"Run completed with status: {run.status}")

# Fetch and log all messages from the thread
messages = project_client.agents.messages.list(thread_id=thread.id)
for message in messages:
    print(f"Role: {message['role']}, Content: {message['content']}")

# Delete the agent after use
project_client.agents.delete_agent(agent.id)
print("Deleted agent")
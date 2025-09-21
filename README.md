# MedicalAgent — Azure AI Foundry Medical Research Agent (POC)

**MedicalAgent** is a proof-of-concept project that demonstrates calling an Azure AI Foundry Agent from Python and integrating a local Wikipedia-style dataset as a tool for medical term lookups. It shows how to handle the agent lifecycle (threads, runs, `requires_action`) and how to confirm whether an answer came from the LLM itself or from the local wiki dataset.

---

## Features
- Create an AI Agent and conversation thread via `azure-ai-projects`.
- Add user messages and trigger agent runs.
- Detect when the agent requests a tool (`requires_action`) and provide tool outputs.
- Local `wikipedia_data.json` (100 terms) used as fast, offline tool.
- Logging to show whether the LLM answered directly or used the local wiki.
- Safe network fallbacks and caching suggestions.

---

## Prerequisites
- Python 3.9+ (virtualenv recommended)
- Azure subscription with AI Foundry / AI Projects access
- Service principal or `az login` for authentication
- Packages:
  ```bash
  pip install azure-identity azure-ai-projects requests

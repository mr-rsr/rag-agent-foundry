# Azure AI Foundry RAG Agent: Knowledge Base, Guardrails & Evaluation

[![Azure AI Foundry](https://img.shields.io/badge/Azure%20AI-Foundry-0078D4?logo=microsoftazure&logoColor=white)](https://ai.azure.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade reference implementation demonstrating the end-to-end lifecycle of a Retrieval-Augmented Generation (RAG) assistant built with **Microsoft Azure AI Foundry**.

This project showcases how to combine **vector-grounded Knowledge Bases**, **autonomous Prompt Agents**, **multi-layer Content Safety Guardrails**, and **systematic evaluation pipelines** for home appliance customer support.

---

## 🏛 Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │               User Query               │
                      └───────────────────┬────────────────────┘
                                          │
                        [ Intercept: Jailbreak & Safety ]
                                          ▼
                      ┌────────────────────────────────────────┐
                      │     Azure AI Foundry Guardrails        │
                      │  • Direct / Indirect Prompt Injection  │
                      │  • Hate / Sexual / Violence / Self-harm│
                      │  • Protected Material & PII Blocking   │
                      └───────────────────┬────────────────────┘
                                          │ (If safe)
                                          ▼
                      ┌────────────────────────────────────────┐
                      │    Agent: `appliancesupport` (GPT-4o)  │
                      │  • Query decomposition & synthesis     │
                      │  • Enforces source citations           │
                      │  • Recommends certified service        │
                      └───────────────────┬────────────────────┘
                                          │
                                   Retrieval Call
                                          ▼
                      ┌────────────────────────────────────────┐
                      │   Knowledge Base: `homeappliancesupportkb`
                      │  • Embedding: text-embedding-3-large   │
                      │  • Source Documents (Manuals, Specs)   │
                      │  • Extractive synthesis & grounding    │
                      └───────────────────┬────────────────────┘
                                          │
                                   Grounding Evidence
                                          ▼
                      ┌────────────────────────────────────────┐
                      │          Grounded Response             │
                      │     with PDF Document Citations        │
                      └────────────────────────────────────────┘
```

---

## 📂 Repository Structure

```
.
├── DATA/
│   ├── AC-2026_merged.pdf                   # Product brochures, cooling capacities & engineering specs
│   ├── Sharp_AC_User_Manual.pdf             # Operating instructions, maintenance guidelines & safety alerts
│   └── Sharp_AC_Warranty_Return_Service.pdf # Model warranty eligibility, returns & service SLA documentation
├── Evals/
│   ├── appliance_support_evaluation.jsonl   # Golden evaluation dataset (queries, ground truth, citations, context)
│   └── data-sample.jsonl                    # Reference format for single-turn evaluation metrics
├── src/
│   ├── __init__.py                          # Package root
│   ├── config.py                            # Foundry prompt configurations, retrieval rules & guardrail policies
│   ├── agent.py                             # ApplianceSupportAgent client with Azure Foundry & offline fallbacks
│   └── eval_runner.py                       # Automated evaluation runner assessing citation coverage & grounding
├── Microsoft Foundry Demo Script_ Knowledge Base, Agent, Guardrails and Evaluation.pdf # Official demo guide
├── requirements.txt                         # Python dependencies
├── .env.example                             # Environment variable template
└── .gitignore                               # Standard Python and credentials ignore file
```

---

## 🚀 The 6-Step Implementation Flow

### Step 1: Deploy Required Models
Deploy two core models inside your Azure AI Foundry Project:
- **Chat Completion Model (`gpt-4o`)**: Responsible for agent reasoning, subquery planning, and synthesis.
- **Embedding Model (`text-embedding-3-large`)**: Converts documentation into high-dimensional vector representations.

---

### Step 2: Configure the Knowledge Base (`homeappliancesupportkb`)
The knowledge base uses **Foundry IQ** to plan subqueries and retrieve extractive data.

- **Name**: `homeappliancesupportkb`
- **Output Mode**: `Extractive data`
- **Reasoning Effort**: `Minimal`
- **Retrieval Instructions**:
  > *"Search the available knowledge sources to find information relevant to the user's question. Identify the relevant product, model, and topic before retrieving information. Break complex questions into focused subqueries when necessary. Prioritize information explicitly supported by the documents. If sources conflict or information is missing, state the limitation rather than guessing."*

**Ingested Sources**:
- `AC-2026_merged.pdf`: Cooling capacities (e.g. Model `AH-SI18V5B-SCN`: 5,210 W), temperature ratings (16°C ~ 55°C).
- `Sharp_AC_User_Manual.pdf`: Maintenance instructions, filter care, electrical safety hazards.
- `Sharp_AC_Warranty_Return_Service.pdf`: 10-year compressor warranty, 7-day return notification, and 14-day return window.

---

### Step 3: Configure the Prompt Agent (`appliancesupport`)
The agent answers customer questions using connected documents and strictly cites evidence.

- **Agent Name**: `appliancesupport`
- **Experience**: `Chat`
- **System Instructions**:
  > *"You are a home appliance support assistant. Answer questions about product specifications, features, operation, maintenance, troubleshooting, and warranty using the connected knowledge base. Base your answers on retrieved information. Provide source citations when available. Ask for the product model when necessary. If information is missing or unclear, state that you cannot confirm it rather than guessing. Give clear, concise, and practical answers. For safety-critical issues, recommend contacting an authorized service professional."*

---

### Step 4: Multi-Layer Guardrail Configuration
Safety controls protect against adversarial manipulation, unsafe guidance, and brand risk:

| Guardrail Type | Intervention Point | Action / Policy |
| :--- | :--- | :--- |
| **Jailbreak Detection** | User Input | **Block** |
| **Indirect Prompt Injection** | User Input & Tool Results | **Block** |
| **Hate / Sexual / Violence / Self-harm** | User Input & Agent Output | **Medium Blocking Threshold** |
| **Protected Material (Text & Code)** | Agent Output | **Block** |
| **Safety-Critical Guidance** | Agent Reasoning | Enforces certified technician handoff |

---

### Step 5: Evaluation & Quality Benchmarking
Evaluation uses individual-turn validation to measure **Answer Relevance**, **Groundedness**, **Instruction Adherence**, and **Safety**.

The included dataset (`Evals/appliance_support_evaluation.jsonl`) contains 10 golden benchmark scenarios covering:
- Specific model lookup & cooling capacities
- Multi-document warranty verification
- Safe maintenance instructions vs electrical hazard refusal
- Out-of-domain rejection (e.g. refrigerator queries answered as unsupported)

---

### Step 6: Production Validation & Results
Run the automated benchmark locally to evaluate grounding and citation adherence:

```bash
python src/eval_runner.py
```

Sample output:
```text
Running Evaluation on 10 sample records...
-----------------------------------------------------------------
[01] Query: What is the cooling capacity of model AH-SI18...
     Citation Present: ✓ | Term Overlap: 80.0%
[02] Query: What is the compressor warranty mentioned in ...
     Citation Present: ✓ | Term Overlap: 63.6%
...
-----------------------------------------------------------------
Evaluation Summary:
  • Total evaluated: 10
  • Citation coverage: 100.0%
  • Grounding alignment: 90.0%
  • Evaluation dataset: Evals/appliance_support_evaluation.jsonl
-----------------------------------------------------------------
```

---

## 🛠 Local Setup & Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/mr-rsr/rag-agent-foundry.git
cd rag-agent-foundry
```

### 2. Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your Azure AI Foundry Project details:
```bash
cp .env.example .env
```

```env
PROJECT_CONNECTION_STRING="<region>.api.azureml.ms;<subscription_id>;<resource_group>;<project_name>"
AZURE_OPENAI_DEPLOYMENT="gpt-4o"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-3-large"
KNOWLEDGE_BASE_NAME="homeappliancesupportkb"
AGENT_NAME="appliancesupport"
```

### 4. Run the Agent Demonstration
```bash
python src/agent.py
```

### 5. Run the Evaluation Suite
```bash
python src/eval_runner.py
```

---

## 📄 License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

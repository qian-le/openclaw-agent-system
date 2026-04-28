# OpenClaw Agent System

> 🚧 **WIP** — This project is under active development.

A lightweight multi-agent orchestration framework built around five specialized agents: **Scout**, **Analyst**, **Guard**, **Executor**, and **Coordinator**. A sixth module, **Hermes**, serves as the decision and policy engine.

Designed to work alongside OpenClaw as an extensible reasoning and execution layer.

---

## Architecture

### Five Agents

| Agent | Responsibility |
|---|---|
| **Scout** | Gathers information: workspace files, memory, web search |
| **Analyst** | Evaluates findings, compares approaches, assesses risks |
| **Guard** | Mandatory safety gate — reviews all execution requests |
| **Executor** | Performs actual operations: file I/O, shell commands |
| **Coordinator** | Classifies tasks, orchestrates pipeline, aggregates results |

### Hermes Decision Module

Hermes is the policy engine at the core of the system:

```python
from hermes import DecisionEngine, DecisionStatus

engine = DecisionEngine()
result = engine.evaluate("delete_file", context={"path": "/tmp/test.txt"})

if result.is_approved():
    print("Proceed")
elif result.is_rejected():
    print("Denied")
```

---

## Current Capabilities (WIP)

- **Task Classification** — Coordinator classifies requests into Info / Analysis / Execution / Risky Execution
- **Agent Pipeline Routing** — Tasks flow through the appropriate agent chain
- **Safety Gate** — Guard blocks destructive and external actions pending confirmation
- **Policy Evaluation** — Hermes provides rule-based decision evaluation
- **Audit Trail** — All Guard reviews and Hermes decisions are logged

---

## Quick Demo

Example task:

> "Create a file test.txt and write 'hello world'"

Execution flow:

1. **Scout** → classify task as `Execution`
2. **Analyst** → generate plan: create file → write content → verify
3. **Guard** → approve operation (internal operations, safe)
4. **Executor** → create `test.txt` with content `hello world`
5. **Coordinator** → return result to user

```python
import asyncio
from multi_agent import Coordinator

async def main():
    coord = Coordinator(workspace_path=".")
    result = await coord.dispatch(
        "Create a file test.txt and write 'hello world'"
    )
    print(result["status"])  # "success"
    print(result["output"])  # "File created: test.txt"

asyncio.run(main())
```

Result:
✅ File `test.txt` successfully created with expected content.

---

## Usage

### Basic Pipeline

```python
import asyncio
from multi_agent import Coordinator

async def main():
    coord = Coordinator(workspace_path="/path/to/workspace")

    # Info task — Scout only
    result = await coord.dispatch("What files are in the workspace?")

    # Execution task — Scout → Analyst → Guard → Executor
    result = await coord.dispatch("Create a summary report at reports/summary.md")

    print(result["status"])

asyncio.run(main())
```

### Using Hermes Directly

```python
from hermes import DecisionEngine, DecisionStatus

engine = DecisionEngine()

# Evaluate an action
result = engine.evaluate("read_file", context={"path": "/data/config.json"})
print(result.status)  # DecisionStatus.APPROVED

# Evaluate a destructive action
result = engine.evaluate("delete_all_logs", context={})
print(result.status)  # DecisionStatus.REJECTED
```

### Registering Custom Policies

```python
from hermes import DecisionEngine, DecisionStatus

engine = DecisionEngine()
engine.add_policy(
    policy_id="beta_feature",
    rules=[{"type": "operation_in", "value": ["beta_"]}],
    default_decision=DecisionStatus.DEFERRED,
    description="Defer beta feature actions for review",
)

result = engine.evaluate("beta_deploy", context={})
print(result.policy_id)  # "beta_feature"
```

---

## Project Structure

```
openclaw-agent-system/
├── multi_agent/           # Agent implementations
│   ├── scout.py           # Scout agent
│   ├── analyst.py         # Analyst agent
│   ├── guard.py           # Guard agent (safety gate)
│   ├── executor.py        # Executor agent
│   └── coordinator.py     # Coordinator (orchestrator)
├── hermes/                # Decision & policy engine
│   └── decision.py        # DecisionEngine + DecisionResult
├── llm/                   # LLM provider interface
│   └── provider.py        # Unified LLM adapter (MiMo/GPT/Claude)
├── examples/              # Usage examples
│   └── demo_task.md       # Demo task walkthrough
├── docs/                  # Documentation
│   └── architecture.md    # System architecture
├── README.md
├── requirements.txt
└── .gitignore
```

---

## 🚧 WIP Status

This project is a **work-in-progress** foundation:

| Component | Status |
|---|---|
| Agent class stubs | ✅ Complete (frameworks + method signatures) |
| Coordinator pipeline | ✅ Complete |
| Hermes decision engine | ✅ Complete |
| Tool integration | ⏳ Planned |
| Persistent state | ⏳ Planned |
| Error recovery | ⏳ Planned |
| MiMo integration | ⏳ Planned |

---

## LLM Integration (Planned)

The system is designed to integrate external LLM APIs.

A unified provider interface is prepared at `llm/provider.py` to support:
- **MiMo API** (primary target)
- GPT / Claude (fallback providers)

LLM will be used in:
- **Analyst** — planning and approach evaluation
- **Hermes** — decision making and policy reasoning
- **Coordinator** — global reasoning and task orchestration

```python
from llm import get_provider

llm = get_provider("mimo")  # or: get_provider("openai")
response = llm.generate("Plan a multi-step file organization task.")
print(response)
```

---

## ⭐ MiMo Integration Plan

This project is designed to integrate MiMo as a reasoning engine for multi-agent workflows. Planned integrations:

### 1. Hermes as MiMo Policy Core
Use MiMo as the reasoning engine behind Hermes decision evaluation — replacing rule-based matching with semantic policy understanding.

### 2. Long-Context Task Planning
MiMo's extended context windows enable the Coordinator to maintain full cross-agent task history and reason about multi-step plans across sessions.

### 3. Multi-Agent Reasoning Enhancement
Enhance the routing and branching logic with MiMo-powered reasoning:
- Dynamic pipeline selection (not fixed by task type)
- Context-aware agent collaboration strategies
- Explainable decision chains with natural language rationale

---

## Dependencies

```
# requirements.txt
aiosignal>=1.3.1
```

Full dependency list: see `requirements.txt`

---

## License

MIT License

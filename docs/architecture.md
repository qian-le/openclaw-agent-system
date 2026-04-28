# Architecture — OpenClaw Agent System

## Overview

The MiMo Multi-Agent System is an orchestration framework built around five specialized agents: **Scout**, **Analyst**, **Guard**, **Executor**, and **Coordinator**. A sixth module, **Hermes**, serves as the decision and policy engine embedded within the Coordinator.

This is a **WIP project** under the MiMo Token application initiative.

---

## Agent Roles

| Agent | Role | Responsibility |
|---|---|---|
| **Scout** | Investigator | Gathers information from workspace, memory, and web |
| **Analyst** | Evaluator | Analyzes findings, compares approaches, assesses risks |
| **Guard** | Gatekeeper | Mandatory safety review before any execution |
| **Executor** | Operator | Performs actual file/command operations |
| **Coordinator** | Orchestrator | Classifies tasks, routes pipeline, aggregates results |
| **Hermes** | Decision Engine | Policy evaluation, routing logic, reasoning core |

---

## Pipeline Architecture

### Task Flow

```
User Request
    │
    ▼
Coordinator.classify(task)
    │
    ├── Info ──────► Scout ──────────────────► Result
    │
    ├── Analysis ──► Scout ─► Analyst ─────► Result
    │
    ├── Execution ─► Scout ─► Analyst ─► Guard ─► Executor ─► Result
    │
    └── Risky ─────► Scout ─► Analyst ─► Guard
                                              │
                                    ┌─────────┴─────────┐
                                    │   APPROVED       │   DENIED
                                    │   continue       │   stop
                                    │                   │
                                    │   NEEDS_CONFIRM  │
                                    │   pause + ask    │
                                    └───────────────────┘
```

### Path Rules

| Task Type | Scout | Analyst | Guard | Executor |
|---|---|---|---|---|
| Info | ✅ | ❌ | ❌ | ❌ |
| Analysis | ✅ | ✅ | ❌ | ❌ |
| Execution | ✅ | ✅ | ✅ | ✅ |
| Risky Execution | ✅ | ✅ | ✅ | ✅ (after user confirm) |

---

## Hermes — Decision Engine Position

Hermes sits at the core of the system as the **policy and reasoning layer**:

```
              ┌─────────────────────────────────────────────┐
              │                   Hermes                     │
              │                                             │
              │  ┌─────────────┐  ┌─────────────────────┐  │
              │  │ Policy Store │  │ Decision Engine     │  │
              │  │              │  │                     │  │
              │  │ safe_internal│  │ evaluate(action,    │  │
              │  │ destructive  │  │   context)          │  │
              │  │ external     │  │                     │  │
              │  └─────────────┘  └─────────────────────┘  │
              └──────────────────────┬──────────────────────┘
                                     │
                     ┌───────────────┼───────────────────────┐
                     │               │                       │
               Guard uses         Coordinator uses       Future:
               for pre-exec       for routing           MiMo reasoning
               policy check        decisions             integration
```

### Hermes Responsibilities

1. **Policy Evaluation** — Match actions against registered policy rules
2. **Decision Output** — Return structured `DecisionResult` with reasons
3. **Confidence Scoring** — Assess decision confidence
4. **Audit Trail** — Log all decisions for review

---

## Decision Flow (Guard + Hermes)

```
Execution Request
    │
    ▼
Guard.review(action, context)
    │
    ├── Consults Hermes Decision Engine
    │
    ├── Hermes.evaluate(action, context)
    │       │
    │       ├── Matches against registered policies
    │       ├── Returns DecisionResult
    │       │
    │       ├── APPROVED → Guard returns approved
    │       ├── REJECTED → Guard returns denied
    │       └── DEFERRED → Guard returns needs_confirmation
    │
    ▼
User (if confirmation required)
```

---

## LLM Integration Layer

The architecture includes an LLM layer that sits across multiple agents:

```
User Input
     │
     ▼
Scout → Analyst → (LLM Reasoning)
     │
     ▼
Hermes (Policy + LLM)
     │
     ▼
Guard → Executor
```

**LLM enhances:**
- **Planning quality** — Analyst uses LLM to generate more robust multi-step plans
- **Long-context reasoning** — Hermes uses LLM to reason over extended context windows
- **Multi-agent coordination** — Coordinator uses LLM for dynamic pipeline branching and strategy selection

The `llm/provider.py` module provides a unified interface for:
- MiMo API (primary target)
- OpenAI GPT (fallback)
- Anthropic Claude (fallback)

---

## Hermes & MiMo Integration (Planned)

Hermes is designed to be the integration point for MiMo capabilities:

### 1. Policy Engine (MiMo as Policy Core)
```
Current: Rule-based policy matching
Planned: MiMo-powered policy reasoning with:
  - Natural language policy definitions
  - Learned policy optimization from past decisions
  - Contextual policy adaptation
```

### 2. Long-Context Task Planning (MiMo Context Windows)
```
Current: Stateless per-agent dispatch
Planned: MiMo maintains cross-agent context:
  - Full task history across all pipeline stages
  - Memory of previous sessions
  - Multi-hop reasoning across Scout→Analyst→Guard
```

### 3. Multi-Agent Reasoning Enhancement
```
Current: Deterministic routing based on task type
Planned: MiMo enhances:
  - Dynamic pipeline branching based on context
  - Agent collaboration strategies
  - Explainable reasoning chains
```

---

## Data Flow

```
Scout findings ──► Analyst ──► Analysis ──┐
                                          ▼
                                     Coordinator
                                          │
                                          ▼
User Request ──► Coordinator ──► Guard ◄──┘
                     │
                     ▼
              Executor (after Guard approval)
                     │
                     ▼
              reports/result ──► User
```

---

## Extensibility

### Adding a New Agent

1. Create `multi_agent/new_agent.py` with class definition
2. Import in `multi_agent/__init__.py`
3. Instantiate in `Coordinator.__init__`
4. Add routing logic in `Coordinator.dispatch`

### Adding a New Policy (Hermes)

```python
engine = DecisionEngine()
engine.add_policy(
    policy_id="my_custom_policy",
    rules=[
        {"type": "operation_in", "value": ["custom_action"]},
    ],
    default_decision=DecisionStatus.APPROVED,
    description="Custom policy for my_action",
)
```

### Adding Task Types

Update `coordinator.py`:
```python
class TaskType:
    INFO = "Info"
    ANALYSIS = "Analysis"
    EXECUTION = "Execution"
    RISKY_EXECUTION = "Risky Execution"
    NEW_TYPE = "New Type"  # add here
```

---

## Current Limitations (WIP)

- All agents are stubs with async method signatures; real integration with tools (memory_search, web_search, exec, etc.) is planned
- Hermes policies are rule-based only; MiMo integration for semantic policy reasoning is planned
- No persistent state between sessions (coordination state lives in-memory)
- No error recovery / retry logic beyond what Coordinator provides
- Guard's safety checks are keyword-based, not semantic

---

## Future Extensions

- [ ] Full tool integration for all agents (real memory_search, web_search, exec)
- [ ] MiMo integration for policy engine enhancement
- [ ] Persistent audit log for all decisions
- [ ] Dynamic pipeline branching (not just fixed task-type routes)
- [ ] Parallel agent execution where dependencies allow
- [ ] Built-in retry and error recovery
- [ ] Observability: tracing, metrics, and decision explainability

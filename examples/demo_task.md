# Demo Task — MiMo Multi-Agent Pipeline

## Scenario: Analyze and create a project report

**User Request:**
> "Analyze the current workspace structure and create a summary report at reports/workspace_summary.md"

---

## Pipeline Walkthrough

### Step 1 — Task Classification (Coordinator)

The Coordinator receives the raw request and classifies it:

```
Task: "Analyze the current workspace structure and create a summary report at reports/workspace_summary.md"
Type: Execution (contains both analysis and creation)
```

The Coordinator determines:
- **Scout** is needed to gather workspace info
- **Analyst** is needed to make sense of the structure
- **Guard** is needed before writing to disk
- **Executor** will perform the file write

---

### Step 2 — Scout: Investigate

Scout searches the workspace:

```
Query: workspace structure, file count, directory tree
Sources: workspace files, memory context

Findings:
  - 47 Python files across 12 directories
  - Active skills in skills/ directory (32 skills)
  - Memory system present (daily/, long-term/)
  - .git directory present (git repo)
  - 3 markdown documentation files
```

Scout returns findings to Coordinator.

---

### Step 3 — Analyst: Analyze

Analyst evaluates the findings:

```
Analysis:
  - Workspace is a mature OpenClaw agent workspace
  - Skills-driven architecture (32 skills)
  - Memory persistence via flat files
  - No obvious structural issues

Recommendations:
  - Workspace structure is healthy
  - Consider consolidating older skills
  - Report path: reports/workspace_summary.md

Risks:
  - reports/ directory may not exist (Executor handles creation)
```

Analyst returns structured analysis to Coordinator.

---

### Step 4 — Guard: Safety Review

Guard reviews the execution request:

```
Action: Write file to reports/workspace_summary.md
Target: reports/workspace_summary.md
Scope: Internal (within workspace)

Review Result: APPROVED
Warnings: []
```

Guard permits the write because:
- Target is internal to workspace
- Not a destructive operation
- No external system involvement

---

### Step 5 — Executor: Write File

Executor performs the file write:

```
Action: write_file
Path: reports/workspace_summary.md
Content: [summary report content]

Result: SUCCESS
Bytes written: 2048
```

---

## Final Result

```
Pipeline: scout → analyst → guard → executor
Status: COMPLETE
Output: reports/workspace_summary.md created
```

## Agent Call Chain (Summary)

```
User
  └── Coordinator (classify: Execution)
        ├── Scout (investigate workspace)
        ├── Analyst (analyze findings)
        ├── Guard (review write action)
        └── Executor (write file)
  └── User (receives result)
```

---

## Another Scenario: Risky Delete

**Request:** "Delete all .pyc files in the workspace"

```
Task Type: Risky Execution

Pipeline:
  ├── Scout: identify targets (all .pyc files)
  ├── Analyst: assess impact (build artifacts, safe to delete)
  ├── Guard: CONFIRMATION REQUIRED
  │   └── "This action will delete N .pyc files. Confirm?"
  └── [User confirms] → Executor → delete
  OR
  └── [User denies] → pipeline stops
```

Guard's `NEEDS_CONFIRMATION` status pauses the pipeline, ensuring no destructive action happens without explicit user approval.

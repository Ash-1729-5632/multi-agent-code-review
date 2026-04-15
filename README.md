# 🔍 Multi-Agent Code Review System (AMACR)

> An AI-powered code review system using 5 specialized agents that automatically detect bugs, security vulnerabilities, performance issues, and code quality problems in Python code.

Built for **INT450 — LLMs and Agentic AI** | SASTRA Deemed University | 2024–25

---

## 🏗️ Architecture

```
Input Code
     │
     ▼
┌─────────────────────────────────────────────┐
│              Orchestrator                   │
│                                             │
│  ┌──────────┐  ┌─────────────┐             │
│  │   Bug    │  │    Code     │             │
│  │Detection │  │   Quality   │             │
│  └──────────┘  └─────────────┘             │
│  ┌──────────┐  ┌─────────────┐             │
│  │Optimiz-  │  │    Best     │             │
│  │ation     │  │  Practices  │             │
│  └──────────┘  └─────────────┘             │
│  ┌────────────────────────────┐            │
│  │  Security (Bandit + LLM)   │            │
│  └────────────────────────────┘            │
│                                             │
│  → Deduplication → Severity Sort           │
└─────────────────────────────────────────────┘
     │
     ▼
Consolidated Report
```

All 5 agents run in **staggered parallel execution** using `asyncio`, then results are deduplicated and sorted by severity.

---

## ✨ Features

- **5 Specialized AI Agents** — each focused on a different review dimension
- **Real Tool Calling** — Security Agent runs Bandit static analyzer before LLM analysis
- **Parallel Execution** — agents run concurrently with staggered starts to avoid rate limits
- **Deduplication** — overlapping findings across agents are merged intelligently
- **Severity Sorting** — HIGH → MEDIUM → LOW, each tagged with source agent
- **Streamlit UI** — 3-tab interface: Code Input, Review Results, Analytics
- **FastAPI Backend** — REST endpoints for `/review`, `/feedback`, `/analytics`
- **GitHub Actions** — auto-triggers on Pull Requests targeting Python files

---

## 🤖 The 5 Agents

| Agent | Detects |
|-------|---------|
| 🐛 Bug Detection | Division by zero, index errors, resource leaks, off-by-one errors |
| ✨ Code Quality | Bad naming, deep nesting, missing docstrings, long functions |
| ⚡ Optimization | O(n²) algorithms, unnecessary loops, inefficient data structures |
| 📚 Best Practices | SOLID violations, missing type hints, hardcoded values, bare excepts |
| 🔒 Security | SQL injection, command injection, hardcoded secrets, eval() misuse |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM Backend | Groq API (llama3-8b-8192) |
| Agent Orchestration | asyncio + ThreadPoolExecutor |
| Security Tool | Bandit (static analyzer) |
| API Backend | FastAPI + Uvicorn |
| Frontend UI | Streamlit |
| CI/CD | GitHub Actions |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A free [Groq API key](https://console.groq.com)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Ash-1729-5632/multi-agent-code-review.git
cd multi-agent-code-review

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file
echo GROQ_API_KEY=your_groq_key_here > .env
```

### Run the Streamlit UI

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

### Run the FastAPI Backend (optional)

```bash
uvicorn api.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`

---

## 📁 Project Structure

```
multi-agent-code-review/
├── agents/
│   ├── schema.py                 # Shared AgentOutput data model
│   ├── bug_detection_agent.py    # Detects logic bugs and errors
│   ├── code_quality_agent.py     # Checks clean code principles
│   ├── optimization_agent.py     # Finds performance issues
│   ├── best_practices_agent.py   # Enforces design principles
│   ├── security_agent.py         # Bandit + LLM security review
│   └── orchestrator.py           # Parallel runner + deduplication
├── api/
│   ├── main.py                   # FastAPI endpoints
│   └── github_review.py          # GitHub Actions runner script
├── tests/
│   ├── test_bug_agent.py
│   ├── test_all_agents.py
│   ├── test_pipeline.py
│   └── test_security_agent.py
├── data/
│   └── sample_code.py            # Buggy test file for demos
├── .github/
│   └── workflows/
│       └── code_review.yml       # GitHub Actions workflow
├── app.py                        # Streamlit UI
├── requirements.txt
└── .env                          # API keys (not committed)
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/review` | Submit code for review, returns full report |
| `POST` | `/feedback` | Record accepted/dismissed feedback on an issue |
| `GET` | `/analytics` | Get aggregated feedback statistics |
| `GET` | `/health` | Health check |

### Example Request

```bash
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{"code": "def divide(a, b):\n    return a/b", "filename": "math.py"}'
```

### Example Response

```json
{
  "filename": "math.py",
  "total_issues": 3,
  "duplicates_removed": 1,
  "total_tokens": 1243,
  "time_taken_seconds": 18.4,
  "agent_summaries": { ... },
  "issues": [
    {
      "line": 2,
      "severity": "high",
      "description": "Division by zero without check",
      "suggestion": "Add if b == 0 check before dividing",
      "source_agent": "bug_detection"
    }
  ]
}
```

---

## 🔄 How Parallel Execution Works

Agents launch with staggered delays to respect Groq's rate limits while still running concurrently:

```
0s  ──► Bug Detection starts
3s  ──► Code Quality starts
6s  ──► Optimization starts
9s  ──► Best Practices starts
12s ──► Security starts
~25s ─► All agents complete
```

This reduces total runtime by ~50% compared to sequential execution.

---

## 🔒 Security Agent — Tool Calling

The Security Agent demonstrates real tool calling — it doesn't rely on the LLM alone:

```
Code Input
    ↓
[Tool Call] Bandit static analyzer runs as subprocess
    ↓
Bandit JSON findings
    ↓
[LLM Call] Groq LLaMA interprets + extends findings
    ↓
Structured security issues
```

---

## 📊 Sample Output

```
Issues before deduplication : 57
Issues after deduplication  : 46
Duplicates removed          : 11
Total tokens used           : 8035
Time taken                  : 46.34s

#1  Line 5  [HIGH]   — bug_detection    → Division by zero without check
#2  Line 11 [HIGH]   — security         → Index out of range without check
#3  Line 20 [HIGH]   — best_practices   → File descriptor leak
#4  Line 53 [HIGH]   — security         → Hardcoded password detected
#5  Line 55 [HIGH]   — optimization     → Command injection via os.system
...
```

---

## 🎓 Academic Context

This project extends the base paper:

> *"AI-powered Code Review with LLMs: Early Results"* — Rasheed et al., 2024 ([arxiv:2404.18496](https://arxiv.org/abs/2404.18496))

**Our contributions beyond the paper:**
1. Added a dedicated **Security Agent** with Bandit tool calling
2. Added an **Orchestrator** for cross-agent deduplication and conflict resolution
3. Implemented **staggered parallel execution** using asyncio
4. Built a **Streamlit analytics dashboard**
5. Added **FastAPI REST backend** and **GitHub Actions CI/CD integration**

---

## 👥 Team

Built as part of INT450 — LLMs and Agentic AI | SASTRA Deemed University | 2024–25

---

## 📄 License

MIT License — free to use and modify.

# agents/security_agent.py

import json
import os
import subprocess
import tempfile
from groq import Groq
from dotenv import load_dotenv
from agents.schema import AgentOutput, Issue

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an expert security engineer specializing in Python application security.
You will be given two things:
1. The original source code
2. JSON output from Bandit, a Python security linter

Your job is to:
- Interpret the Bandit findings in plain English
- Identify any additional security issues Bandit may have missed such as:
  - Hardcoded passwords, API keys, or secrets
  - SQL injection risks
  - Insecure use of eval() or exec()
  - Unvalidated user input being used in dangerous operations

You must respond ONLY with a valid JSON object in this exact format:
{
  "issues": [
    {
      "line": <line number as integer>,
      "severity": "<high|medium|low>",
      "description": "<what the security issue is>",
      "suggestion": "<how to fix it>"
    }
  ],
  "summary": "<one sentence summary of security findings>"
}

If no issues are found, return an empty issues list.
Do not include any text outside the JSON.
"""

def _run_bandit(code: str) -> dict:
    """
    Writes code to a temp file, runs Bandit on it, returns parsed JSON output.
    """
    # Write code to a temporary file (Bandit needs a real file to scan)
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8'
    ) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["bandit", "-r", tmp_path, "-f", "json", "-q"],
            capture_output=True,
            text=True
        )
        # Bandit returns exit code 1 if it finds issues — that's normal
        bandit_output = json.loads(result.stdout) if result.stdout else {}
    except Exception as e:
        print(f"[SecurityAgent] Bandit error: {e}")
        bandit_output = {}
    finally:
        os.unlink(tmp_path)  # Clean up the temp file

    return bandit_output


def run_security_agent(code: str) -> AgentOutput:
    """
    Runs Bandit on the code, then uses LLM to explain and extend findings.

    Args:
        code: The source code string to review

    Returns:
        AgentOutput with all detected security issues
    """

    # Step 1: Run Bandit (the tool call)
    print("    [Security] Running Bandit static analysis...")
    bandit_results = _run_bandit(code)

    # Summarize Bandit findings to pass to LLM
    bandit_summary = json.dumps(bandit_results, indent=2) if bandit_results else "Bandit found no issues."

    # Step 2: Pass Bandit results + code to LLM for deeper analysis
    user_message = f"""
Here is the source code to review:
```python
{code}
```

Here is the Bandit static analysis output:
```json
{bandit_summary}
```

Based on both the code and the Bandit findings, identify all security issues.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.1,
        max_tokens=1024
    )

    raw = response.choices[0].message.content
    tokens = response.usage.total_tokens

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(f"[SecurityAgent] Warning: Could not parse JSON. Raw output:\n{raw}")
        return AgentOutput(
            agent_name="security",
            issues=[],
            summary="Agent returned unparseable output.",
            tokens_used=tokens
        )

    issues = [
        Issue(
            line=item.get("line", 0),
            severity=item.get("severity", "low"),
            description=item.get("description", ""),
            suggestion=item.get("suggestion", "")
        )
        for item in data.get("issues", [])
    ]

    return AgentOutput(
        agent_name="security",
        issues=issues,
        summary=data.get("summary", "No summary provided."),
        tokens_used=tokens
    )
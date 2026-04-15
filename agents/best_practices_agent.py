# agents/best_practices_agent.py

import json
import os
from groq import Groq
from dotenv import load_dotenv
from agents.schema import AgentOutput, Issue

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an expert software engineer specializing in software design principles and best practices.
Your job is to analyze code and find violations of:
- SOLID principles (Single Responsibility, Open/Closed, etc.)
- DRY principle (Don't Repeat Yourself)
- Missing type hints on function parameters and return types
- Missing or incomplete docstrings on functions and classes
- Bare except clauses (catching all exceptions blindly)
- Hardcoded values that should be constants or config
- Functions with too many parameters (more than 4)

You must respond ONLY with a valid JSON object in this exact format:
{
  "issues": [
    {
      "line": <line number as integer>,
      "severity": "<high|medium|low>",
      "description": "<what best practice is violated>",
      "suggestion": "<how to fix it>"
    }
  ],
  "summary": "<one sentence summary of best practice findings>"
}

If no issues are found, return an empty issues list.
Do not include any text outside the JSON.
"""

def run_best_practices_agent(code: str) -> AgentOutput:
    """
    Analyzes the given code for best practice violations.

    Args:
        code: The source code string to review

    Returns:
        AgentOutput with all detected best practice issues
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Review this code for best practice violations:\n\n```python\n{code}\n```"}
        ],
        temperature=0.1,
        max_tokens=1024
    )

    raw = response.choices[0].message.content
    tokens = response.usage.total_tokens

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(f"[BestPracticesAgent] Warning: Could not parse JSON. Raw output:\n{raw}")
        return AgentOutput(
            agent_name="best_practices",
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
        agent_name="best_practices",
        issues=issues,
        summary=data.get("summary", "No summary provided."),
        tokens_used=tokens
    )
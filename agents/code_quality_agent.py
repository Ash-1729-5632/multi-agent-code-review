# agents/code_quality_agent.py

import json
import os
from groq import Groq
from dotenv import load_dotenv
from agents.schema import AgentOutput, Issue

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an expert software engineer specializing in code quality and clean code principles.
Your job is to analyze code and find:
- Poor naming (vague variable/function names like x, temp, foo)
- Functions that are too long or do too many things
- Duplicate or repeated code blocks
- Missing or inadequate comments/docstrings
- Deep nesting (more than 3 levels of indentation)
- Violation of single responsibility principle

You must respond ONLY with a valid JSON object in this exact format:
{
  "issues": [
    {
      "line": <line number as integer>,
      "severity": "<high|medium|low>",
      "description": "<what the quality issue is>",
      "suggestion": "<how to improve it>"
    }
  ],
  "summary": "<one sentence summary of code quality findings>"
}

If no issues are found, return an empty issues list.
Do not include any text outside the JSON.
"""

def run_code_quality_agent(code: str) -> AgentOutput:
    """
    Analyzes the given code for quality and clean code issues.

    Args:
        code: The source code string to review

    Returns:
        AgentOutput with all detected quality issues
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Review this code for quality issues:\n\n```python\n{code}\n```"}
        ],
        temperature=0.1,
        max_tokens=1024
    )

    raw = response.choices[0].message.content
    tokens = response.usage.total_tokens

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(f"[CodeQualityAgent] Warning: Could not parse JSON. Raw output:\n{raw}")
        return AgentOutput(
            agent_name="code_quality",
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
        agent_name="code_quality",
        issues=issues,
        summary=data.get("summary", "No summary provided."),
        tokens_used=tokens
    )
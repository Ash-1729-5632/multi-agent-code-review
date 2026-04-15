# agents/optimization_agent.py

import json
import os
from groq import Groq
from dotenv import load_dotenv
from agents.schema import AgentOutput, Issue

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an expert software engineer specializing in code performance and optimization.
Your job is to analyze code and find:
- Inefficient algorithms (e.g. O(n^2) where O(n) is possible)
- Unnecessary loops or repeated computation inside loops
- Inefficient data structure choices (e.g. list when a set would be faster)
- Memory waste (storing large data unnecessarily)
- Missing caching for repeated expensive operations
- Unnecessary function calls inside loops

You must respond ONLY with a valid JSON object in this exact format:
{
  "issues": [
    {
      "line": <line number as integer>,
      "severity": "<high|medium|low>",
      "description": "<what the performance issue is>",
      "suggestion": "<how to optimize it>"
    }
  ],
  "summary": "<one sentence summary of optimization findings>"
}

If no issues are found, return an empty issues list.
Do not include any text outside the JSON.
"""

def run_optimization_agent(code: str) -> AgentOutput:
    """
    Analyzes the given code for performance and optimization issues.

    Args:
        code: The source code string to review

    Returns:
        AgentOutput with all detected optimization issues
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Review this code for performance issues:\n\n```python\n{code}\n```"}
        ],
        temperature=0.1,
        max_tokens=1024
    )

    raw = response.choices[0].message.content
    tokens = response.usage.total_tokens

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(f"[OptimizationAgent] Warning: Could not parse JSON. Raw output:\n{raw}")
        return AgentOutput(
            agent_name="optimization",
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
        agent_name="optimization",
        issues=issues,
        summary=data.get("summary", "No summary provided."),
        tokens_used=tokens
    )
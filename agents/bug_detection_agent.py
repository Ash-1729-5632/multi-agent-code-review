# agents/bug_detection_agent.py

import json
import os
from groq import Groq
from dotenv import load_dotenv
from agents.schema import AgentOutput, Issue

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an expert software engineer specializing in bug detection.
Your job is to analyze code and find:
- Logic errors and off-by-one mistakes
- Null/None reference risks
- Unhandled exceptions
- Incorrect conditionals
- Resource leaks (files, connections not closed)

You must respond ONLY with a valid JSON object in this exact format:
{
  "issues": [
    {
      "line": <line number as integer>,
      "severity": "<high|medium|low>",
      "description": "<what the bug is>",
      "suggestion": "<how to fix it>"
    }
  ],
  "summary": "<one sentence summary of findings>"
}

If no bugs are found, return an empty issues list.
Do not include any text outside the JSON.
"""

def run_bug_detection_agent(code: str) -> AgentOutput:
    """
    Analyzes the given code for bugs.
    
    Args:
        code: The source code string to review
        
    Returns:
        AgentOutput with all detected bugs
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Review this code for bugs:\n\n```python\n{code}\n```"}
        ],
        temperature=0.1,   # Low temperature = more consistent, less creative
        max_tokens=1024
    )

    raw = response.choices[0].message.content
    tokens = response.usage.total_tokens

    # Parse the JSON response from the LLM
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # If LLM returns something other than clean JSON, handle gracefully
        print(f"[BugAgent] Warning: Could not parse JSON. Raw output:\n{raw}")
        return AgentOutput(
            agent_name="bug_detection",
            issues=[],
            summary="Agent returned unparseable output.",
            tokens_used=tokens
        )

    # Convert raw dicts into Issue objects
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
        agent_name="bug_detection",
        issues=issues,
        summary=data.get("summary", "No summary provided."),
        tokens_used=tokens
    )
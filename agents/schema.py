# agents/schema.py
# This is the shared output format ALL agents must return.
# Do not change this without telling your teammates — 
# their agents depend on this exact structure.

from dataclasses import dataclass, field
from typing import List

@dataclass
class Issue:
    line: int           # Line number where the issue was found
    severity: str       # "high", "medium", or "low"
    description: str    # What the problem is
    suggestion: str     # How to fix it

@dataclass
class AgentOutput:
    agent_name: str          # e.g. "bug_detection"
    issues: List[Issue]      # List of issues found
    summary: str             # One-line summary of the review
    tokens_used: int         # For cost tracking

    def to_dict(self):
        return {
            "agent_name": self.agent_name,
            "issues": [
                {
                    "line": i.line,
                    "severity": i.severity,
                    "description": i.description,
                    "suggestion": i.suggestion
                }
                for i in self.issues
            ],
            "summary": self.summary,
            "tokens_used": self.tokens_used
        }
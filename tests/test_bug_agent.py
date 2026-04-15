# tests/test_bug_agent.py

from agents.bug_detection_agent import run_bug_detection_agent
import json

# import sys
# import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_bug_detection():
    # Load the sample buggy code
    with open("data/sample_code.py", "r") as f:
        code = f.read()

    print("\n--- Running Bug Detection Agent ---\n")
    result = run_bug_detection_agent(code)

    print(f"Agent: {result.agent_name}")
    print(f"Summary: {result.summary}")
    print(f"Tokens used: {result.tokens_used}")
    print(f"Issues found: {len(result.issues)}\n")

    for issue in result.issues:
        print(f"  Line {issue.line} [{issue.severity.upper()}]")
        print(f"  Problem: {issue.description}")
        print(f"  Fix: {issue.suggestion}")
        print()

    # Basic assertions
    assert result.agent_name == "bug_detection"
    assert isinstance(result.issues, list)
    assert result.tokens_used > 0

    print("✅ All assertions passed!")

if __name__ == "__main__":
    test_bug_detection()
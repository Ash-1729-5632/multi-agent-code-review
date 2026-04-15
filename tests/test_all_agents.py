# tests/test_all_agents.py

from agents.bug_detection_agent import run_bug_detection_agent
from agents.code_quality_agent import run_code_quality_agent
from agents.optimization_agent import run_optimization_agent

def test_all_agents():
    with open("data/sample_code.py", "r") as f:
        code = f.read()

    agents = [
        ("Bug Detection",  run_bug_detection_agent),
        ("Code Quality",   run_code_quality_agent),
        ("Optimization",   run_optimization_agent),
    ]

    total_tokens = 0

    for name, agent_fn in agents:
        print(f"\n{'='*45}")
        print(f"  {name} Agent")
        print(f"{'='*45}")

        result = agent_fn(code)

        print(f"Summary   : {result.summary}")
        print(f"Issues    : {len(result.issues)}")
        print(f"Tokens    : {result.tokens_used}")
        total_tokens += result.tokens_used

        for issue in result.issues:
            print(f"\n  Line {issue.line} [{issue.severity.upper()}]")
            print(f"  Problem : {issue.description}")
            print(f"  Fix     : {issue.suggestion}")

    print(f"\n{'='*45}")
    print(f"  TOTAL TOKENS USED: {total_tokens}")
    print(f"{'='*45}\n")
    print("✅ All agents ran successfully!")

if __name__ == "__main__":
    test_all_agents()
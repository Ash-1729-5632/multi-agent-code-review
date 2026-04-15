# tests/test_security_agent.py

from agents.security_agent import run_security_agent

def test_security_agent():
    with open("data/sample_code.py", "r") as f:
        code = f.read()

    print("\n--- Running Security Agent ---\n")
    result = run_security_agent(code)

    print(f"Agent   : {result.agent_name}")
    print(f"Summary : {result.summary}")
    print(f"Tokens  : {result.tokens_used}")
    print(f"Issues  : {len(result.issues)}\n")

    for issue in result.issues:
        print(f"  Line {issue.line} [{issue.severity.upper()}]")
        print(f"  Problem : {issue.description}")
        print(f"  Fix     : {issue.suggestion}")
        print()

    assert result.agent_name == "security"
    assert isinstance(result.issues, list)
    print("✅ Security agent test passed!")

if __name__ == "__main__":
    test_security_agent()
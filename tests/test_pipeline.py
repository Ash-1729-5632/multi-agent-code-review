# tests/test_pipeline.py

from agents.orchestrator import run_pipeline

def test_pipeline():
    with open("data/sample_code.py", "r") as f:
        code = f.read()

    print("\n🚀 Starting Multi-Agent Code Review Pipeline...\n")
    report = run_pipeline(code)

    print("\n" + "="*50)
    print("         FINAL CONSOLIDATED REPORT")
    print("="*50)

    print("\n📋 Agent Summaries:")
    for agent, summary in report.agent_summaries.items():
        print(f"  [{agent}] {summary}")

    print(f"\n📊 Stats:")
    print(f"  Issues before deduplication : {report.total_issues_before_dedup}")
    print(f"  Issues after deduplication  : {report.total_issues_after_dedup}")
    print(f"  Duplicates removed          : {report.total_issues_before_dedup - report.total_issues_after_dedup}")
    print(f"  Total tokens used           : {report.total_tokens}")
    print(f"  Time taken                  : {report.time_taken_seconds}s")

    print(f"\n🔍 Final Issue List (sorted by severity):")
    for i, issue in enumerate(report.issues, 1):
        print(f"\n  #{i} Line {issue['line']} [{issue['severity'].upper()}] — from {issue['source_agent']}")
        print(f"  Problem : {issue['description']}")
        print(f"  Fix     : {issue['suggestion']}")

    print("\n" + "="*50)
    print("✅ Pipeline completed successfully!")

if __name__ == "__main__":
    test_pipeline()
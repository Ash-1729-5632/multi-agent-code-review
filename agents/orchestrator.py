# agents/orchestrator.py

import asyncio
import time
from dataclasses import dataclass
from typing import List
from concurrent.futures import ThreadPoolExecutor

from agents.bug_detection_agent import run_bug_detection_agent
from agents.code_quality_agent import run_code_quality_agent
from agents.optimization_agent import run_optimization_agent
from agents.best_practices_agent import run_best_practices_agent
from agents.security_agent import run_security_agent
from agents.schema import AgentOutput

SEVERITY_RANK = {"high": 3, "medium": 2, "low": 1}

@dataclass
class FinalReport:
    issues: List[dict]
    agent_summaries: dict
    total_tokens: int
    total_issues_before_dedup: int
    total_issues_after_dedup: int
    time_taken_seconds: float


def _is_duplicate(issue_a: dict, issue_b: dict, line_tolerance: int = 2) -> bool:
    line_close = abs(issue_a["line"] - issue_b["line"]) <= line_tolerance
    stopwords = {"the", "a", "an", "in", "is", "of", "to", "and", "or", "for"}
    words_a = set(issue_a["description"].lower().split()) - stopwords
    words_b = set(issue_b["description"].lower().split()) - stopwords
    keyword_overlap = len(words_a & words_b) >= 2
    return line_close and keyword_overlap


def _deduplicate(all_issues: List[dict]) -> List[dict]:
    unique = []
    for candidate in all_issues:
        is_dup = False
        for kept in unique:
            if _is_duplicate(candidate, kept):
                if SEVERITY_RANK.get(candidate["severity"], 0) > SEVERITY_RANK.get(kept["severity"], 0):
                    kept.update(candidate)
                is_dup = True
                break
        if not is_dup:
            unique.append(candidate)
    return unique


# ─────────────────────────────────────────
# Each agent is wrapped with a staggered
# delay to avoid Groq rate limits while
# still running concurrently
# ─────────────────────────────────────────

async def _run_agent_async(
    name: str,
    agent_fn,
    code: str,
    delay: float,
    executor: ThreadPoolExecutor
) -> AgentOutput:
    """
    Waits `delay` seconds, then runs the agent in a thread pool
    so it doesn't block the event loop.
    """
    await asyncio.sleep(delay)
    print(f"  [START] {name} agent...")
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, agent_fn, code)
    print(f"  [DONE]  {name} agent — {len(result.issues)} issues, {result.tokens_used} tokens")
    return result


def run_pipeline(code: str) -> FinalReport:
    """
    Runs all 5 agents with staggered parallel execution.
    Agents start at different times to avoid Groq rate limits,
    but run concurrently — total time is much less than sequential.

    Stagger schedule:
      Bug Detection   → starts at 0s
      Code Quality    → starts at 3s
      Optimization    → starts at 6s
      Best Practices  → starts at 9s
      Security        → starts at 12s
    """
    start = time.time()

    print("\n🚀 Launching all 5 agents (staggered parallel mode)...\n")

    async def run_all():
        # Thread pool so blocking Groq HTTP calls don't block event loop
        with ThreadPoolExecutor(max_workers=5) as executor:
            tasks = [
                _run_agent_async("Bug Detection",   run_bug_detection_agent,  code, delay=0,  executor=executor),
                _run_agent_async("Code Quality",    run_code_quality_agent,   code, delay=3,  executor=executor),
                _run_agent_async("Optimization",    run_optimization_agent,   code, delay=6,  executor=executor),
                _run_agent_async("Best Practices",  run_best_practices_agent, code, delay=9,  executor=executor),
                _run_agent_async("Security",        run_security_agent,       code, delay=12, executor=executor),
            ]
            # Run all tasks concurrently, gather results
            results = await asyncio.gather(*tasks)
        return results

    all_outputs: List[AgentOutput] = asyncio.run(run_all())

    # Flatten all issues
    all_issues = []
    for output in all_outputs:
        for issue in output.issues:
            all_issues.append({
                "line": issue.line,
                "severity": issue.severity,
                "description": issue.description,
                "suggestion": issue.suggestion,
                "source_agent": output.agent_name
            })

    total_before = len(all_issues)
    unique_issues = _deduplicate(all_issues)
    unique_issues.sort(
        key=lambda x: (-SEVERITY_RANK.get(x["severity"], 0), x["line"])
    )

    total_tokens = sum(o.tokens_used for o in all_outputs)
    elapsed = round(time.time() - start, 2)

    print(f"\n✅ All agents complete in {elapsed}s")

    return FinalReport(
        issues=unique_issues,
        agent_summaries={o.agent_name: o.summary for o in all_outputs},
        total_tokens=total_tokens,
        total_issues_before_dedup=total_before,
        total_issues_after_dedup=len(unique_issues),
        time_taken_seconds=elapsed
    )
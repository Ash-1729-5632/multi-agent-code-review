# api/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.orchestrator import run_pipeline

app = FastAPI(
    title="Multi-Agent Code Review API",
    description="5-agent AI system for automated code review",
    version="1.0.0"
)

# Allow requests from Streamlit and GitHub Actions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ─────────────────────────────────────────
# Request / Response models
# ─────────────────────────────────────────

class ReviewRequest(BaseModel):
    code: str
    filename: Optional[str] = "unnamed.py"

class FeedbackRequest(BaseModel):
    issue_description: str
    action: str          # "accepted", "dismissed", "modified"
    agent_name: str

# In-memory store for feedback (simple for now)
feedback_log = []

# ─────────────────────────────────────────
# Routes
# ─────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "Multi-Agent Code Review API is running",
        "endpoints": ["/review", "/feedback", "/analytics", "/health"]
    }

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/review")
def review_code(request: ReviewRequest):
    """
    Accepts Python code, runs all 5 agents, returns consolidated report.
    """
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    try:
        report = run_pipeline(request.code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

    return {
        "filename": request.filename,
        "total_issues": report.total_issues_after_dedup,
        "duplicates_removed": report.total_issues_before_dedup - report.total_issues_after_dedup,
        "total_tokens": report.total_tokens,
        "time_taken_seconds": report.time_taken_seconds,
        "agent_summaries": report.agent_summaries,
        "issues": report.issues
    }


@app.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    """
    Records developer feedback on a review suggestion.
    Used for tracking which agent suggestions are accepted vs dismissed.
    """
    if request.action not in ["accepted", "dismissed", "modified"]:
        raise HTTPException(
            status_code=400,
            detail="Action must be: accepted, dismissed, or modified"
        )

    entry = {
        "agent": request.agent_name,
        "issue": request.issue_description,
        "action": request.action
    }
    feedback_log.append(entry)

    return {"message": "Feedback recorded", "entry": entry}


@app.get("/analytics")
def get_analytics():
    """
    Returns aggregated statistics from the feedback log.
    """
    if not feedback_log:
        return {
            "total_feedback": 0,
            "acceptance_rate": 0,
            "by_agent": {}
        }

    total = len(feedback_log)
    accepted = sum(1 for f in feedback_log if f["action"] == "accepted")

    # Count feedback per agent
    by_agent = {}
    for entry in feedback_log:
        agent = entry["agent"]
        if agent not in by_agent:
            by_agent[agent] = {"accepted": 0, "dismissed": 0, "modified": 0}
        by_agent[agent][entry["action"]] += 1

    return {
        "total_feedback": total,
        "acceptance_rate": round(accepted / total * 100, 1),
        "by_agent": by_agent,
        "raw_log": feedback_log
    }
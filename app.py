# app.py

import streamlit as st
import sys
import os

# So Python can find your agents/ folder
sys.path.insert(0, os.path.dirname(__file__))

from agents.orchestrator import run_pipeline

# ─────────────────────────────────────────
# Page config
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Code Review",
    page_icon="🔍",
    layout="wide"
)

# ─────────────────────────────────────────
# Header
# ─────────────────────────────────────────
st.title("🔍 Multi-Agent Code Review System")
st.markdown(
    "Powered by **5 specialized AI agents**: "
    "Bug Detection · Code Quality · Optimization · Best Practices · Security"
)
st.divider()

# ─────────────────────────────────────────
# Sidebar — controls
# ─────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    show_low = st.checkbox("Show LOW severity issues", value=True)
    show_medium = st.checkbox("Show MEDIUM severity issues", value=True)
    show_high = st.checkbox("Show HIGH severity issues", value=True)
    st.divider()
    st.markdown("**Severity Legend**")
    st.error("🔴 HIGH — Fix immediately")
    st.warning("🟡 MEDIUM — Fix soon")
    st.info("🔵 LOW — Minor improvement")

# ─────────────────────────────────────────
# Tab layout
# ─────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📝 Code Input", "📊 Review Results", "📈 Analytics"])

# ════════════════════════════════════════
# TAB 1 — Code Input
# ════════════════════════════════════════
with tab1:
    st.subheader("Paste your Python code below")

    # Pre-fill with a simple buggy example so the user can test immediately
    default_code = '''def divide(a, b):
    return a / b  # Bug: no zero check

def read_file(path):
    f = open(path)
    return f.read()  # Bug: file never closed

PASSWORD = "secret123"  # Security: hardcoded secret

def find_item(items, target):
    for i in range(len(items) + 1):  # Bug: off-by-one
        if items[i] == target:
            return i
'''

    code_input = st.text_area(
        label="Source Code",
        value=default_code,
        height=350,
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        run_button = st.button("🚀 Run Review", type="primary", use_container_width=True)
    with col2:
        st.caption("Running all 5 agents takes ~30–60 seconds on first run.")

# ════════════════════════════════════════
# TAB 2 — Review Results
# ════════════════════════════════════════
with tab2:

    if run_button:
        if not code_input.strip():
            st.error("Please paste some code in the Code Input tab first.")
        else:
            # Run the pipeline with a progress indicator
            with st.spinner("Running 5 agents... this takes about 30–60 seconds"):
                report = run_pipeline(code_input)

            # Store in session state so results persist when switching tabs
            st.session_state["report"] = report
            st.success(f"✅ Review complete in {report.time_taken_seconds}s")

    if "report" in st.session_state:
        report = st.session_state["report"]

        # ── Agent summaries ──────────────────────
        st.subheader("🧠 Agent Summaries")
        agent_icons = {
            "bug_detection":  "🐛",
            "code_quality":   "✨",
            "optimization":   "⚡",
            "best_practices": "📚",
            "security":       "🔒"
        }
        cols = st.columns(len(report.agent_summaries))
        for col, (agent, summary) in zip(cols, report.agent_summaries.items()):
            with col:
                icon = agent_icons.get(agent, "🤖")
                st.metric(
                    label=f"{icon} {agent.replace('_', ' ').title()}",
                    value=f"{sum(1 for i in report.issues if i['source_agent'] == agent)} issues"
                )
                st.caption(summary)

        st.divider()

        # ── Issue list ───────────────────────────
        st.subheader(f"🔍 Issues Found ({report.total_issues_after_dedup} unique)")

        # Apply sidebar filters
        severity_filter = []
        if show_high:   severity_filter.append("high")
        if show_medium: severity_filter.append("medium")
        if show_low:    severity_filter.append("low")

        filtered = [i for i in report.issues if i["severity"] in severity_filter]

        if not filtered:
            st.info("No issues match the selected severity filters.")
        else:
            for issue in filtered:
                sev = issue["severity"]
                icon = "🔴" if sev == "high" else ("🟡" if sev == "medium" else "🔵")
                agent = issue["source_agent"].replace("_", " ").title()

                with st.expander(
                    f"{icon} Line {issue['line']} [{sev.upper()}] — {issue['description'][:60]}..."
                    if len(issue['description']) > 60
                    else f"{icon} Line {issue['line']} [{sev.upper()}] — {issue['description']}"
                ):
                    st.markdown(f"**Detected by:** `{agent}`")
                    st.markdown(f"**Problem:** {issue['description']}")
                    st.markdown(f"**Suggested Fix:** {issue['suggestion']}")

    else:
        st.info("👈 Go to the **Code Input** tab, paste your code, and click **Run Review**.")

# ════════════════════════════════════════
# TAB 3 — Analytics
# ════════════════════════════════════════
with tab3:

    if "report" in st.session_state:
        report = st.session_state["report"]

        # ── Top metrics ──────────────────────────
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Issues", report.total_issues_after_dedup)
        col2.metric("Duplicates Removed", report.total_issues_before_dedup - report.total_issues_after_dedup)
        col3.metric("Tokens Used", f"{report.total_tokens:,}")
        col4.metric("Time Taken", f"{report.time_taken_seconds}s")

        st.divider()

        # ── Severity breakdown chart ─────────────
        st.subheader("📊 Issues by Severity")

        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for issue in report.issues:
            severity_counts[issue["severity"].upper()] += 1

        # Use Streamlit's built-in bar chart
        st.bar_chart(severity_counts)

        st.divider()

        # ── Issues per agent chart ───────────────
        st.subheader("🤖 Issues Detected per Agent")

        agent_counts = {}
        for issue in report.issues:
            agent = issue["source_agent"].replace("_", " ").title()
            agent_counts[agent] = agent_counts.get(agent, 0) + 1

        st.bar_chart(agent_counts)

        st.divider()

        # ── Raw data table ───────────────────────
        st.subheader("📋 Full Issue Table")
        import pandas as pd

        df = pd.DataFrame(report.issues)
        df = df.rename(columns={
            "line": "Line",
            "severity": "Severity",
            "description": "Problem",
            "suggestion": "Fix",
            "source_agent": "Agent"
        })
        st.dataframe(df, use_container_width=True)

    else:
        st.info("👈 Run a review first to see analytics.")
"""
PhishGuard — Streamlit App
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
from detector import analyse

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PhishGuard",
    page_icon="🛡️",
    layout="centered"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main { background-color: #0a0c10; }

h1, h2, h3 {
    font-family: 'Space Mono', monospace !important;
}

.stTextArea textarea {
    background-color: #111520 !important;
    color: #e2e8f0 !important;
    border: 1px solid #1e2535 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 13px !important;
}

.risk-card {
    padding: 24px;
    border-radius: 12px;
    border: 2px solid;
    text-align: center;
    margin-bottom: 20px;
}

.flag-item {
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 8px;
    border-left: 4px solid;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🛡️ PhishGuard")
st.markdown("**Phishing Detection Tool** — Analyse URLs and email content for suspicious indicators.")
st.divider()

# ── Risk Level Colors ─────────────────────────────────────────────────────────
RISK_COLORS = {
    "Safe":     "#22c55e",
    "Low":      "#84cc16",
    "Medium":   "#f59e0b",
    "High":     "#f97316",
    "Critical": "#ef4444",
}

RISK_EMOJI = {
    "Safe":     "✅",
    "Low":      "🟡",
    "Medium":   "🟠",
    "High":     "🔴",
    "Critical": "🚨",
}

# ── Example Inputs ────────────────────────────────────────────────────────────
st.markdown("#### Try an example:")
col1, col2, col3 = st.columns(3)

examples = {
    "Safe URL":       "https://www.google.com/search?q=cybersecurity",
    "Phishing URL":   "http://paypa1-secure-verify.tk/login?ref=account&update=true",
    "Phishing Email": "From: security@paypa1-support.com\n\nDear Customer,\n\nWe have detected unusual activity on your account. Your account will be suspended within 24 hours unless you verify your account immediately.\n\nClick here: http://paypa1-verify.ml/secure-login\n\nFailure to act now will result in permanent account closure."
}

if col1.button("✅ Safe URL"):
    st.session_state.input_text = examples["Safe URL"]
if col2.button("🎣 Phishing URL"):
    st.session_state.input_text = examples["Phishing URL"]
if col3.button("📧 Phishing Email"):
    st.session_state.input_text = examples["Phishing Email"]

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("#### Paste a URL or Email Body:")
input_text = st.text_area(
    label="input",
    label_visibility="collapsed",
    placeholder="e.g. http://paypa1-secure.tk/login   or paste a full email body...",
    value=st.session_state.get("input_text", ""),
    height=150
)

analyse_btn = st.button("🔍 Analyse", type="primary", use_container_width=True)

# ── Analysis ──────────────────────────────────────────────────────────────────
if analyse_btn:
    if not input_text.strip():
        st.warning("Please paste a URL or email body first.")
    else:
        with st.spinner("Analysing..."):
            result = analyse(input_text.strip())

        st.divider()
        st.markdown("### Results")

        # Risk score + level
        color = RISK_COLORS[result.risk_level]
        emoji = RISK_EMOJI[result.risk_level]

        col_a, col_b = st.columns(2)
        col_a.metric("Risk Score", f"{result.risk_score} / 100")
        col_b.metric("Risk Level", f"{emoji} {result.risk_level}")

        # Progress bar
        st.progress(result.risk_score / 100)

        # Input type
        st.caption(f"Detected input type: **{result.input_type.upper()}**")

        st.divider()

        # Flags
        if result.flags:
            st.markdown(f"#### ⚠️ {len(result.flags)} Indicator(s) Found")
            for flag in result.flags:
                st.error(f"⚠ {flag}")
        else:
            st.success("✅ No suspicious indicators detected. This looks clean!")

        # Details
        if result.details:
            with st.expander("🔎 Analysis Details"):
                for key, val in result.details.items():
                    if isinstance(val, list):
                        st.markdown(f"**{key.replace('_', ' ').title()}:** {', '.join(val)}")
                    else:
                        st.markdown(f"**{key.replace('_', ' ').title()}:** `{val}`")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("🛡️ PhishGuard · Built with Python & Streamlit · For educational purposes only")

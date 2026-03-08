"""
PhishGuard — Streamlit App (Redesigned)
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
    background-color: #0a0c10 !important;
    color: #e2e8f0 !important;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

.block-container {
    padding: 2rem 2rem 4rem !important;
    max-width: 780px !important;
}

.stTextArea textarea {
    background-color: #111520 !important;
    color: #e2e8f0 !important;
    border: 1px solid #1e2535 !important;
    border-radius: 10px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 13px !important;
    padding: 14px !important;
    caret-color: #00e5ff;
}

.stTextArea textarea:focus {
    border-color: #00e5ff !important;
    box-shadow: 0 0 0 1px #00e5ff22 !important;
}

.stButton > button {
    background: #00e5ff !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 12px 24px !important;
    width: 100%;
    letter-spacing: 0.3px;
}

.stButton > button:hover {
    background: #29f0ff !important;
    transform: translateY(-1px) !important;
}

div[data-testid="column"] .stButton > button {
    background: #111520 !important;
    color: #94a3b8 !important;
    border: 1px solid #1e2535 !important;
    font-size: 12px !important;
    padding: 8px 12px !important;
}

div[data-testid="column"] .stButton > button:hover {
    border-color: #00e5ff !important;
    color: #00e5ff !important;
    background: #111520 !important;
}

hr { border-color: #1e2535 !important; margin: 24px 0 !important; }
</style>
""", unsafe_allow_html=True)

RISK_COLORS = {
    "Safe": "#22c55e", "Low": "#84cc16",
    "Medium": "#f59e0b", "High": "#f97316", "Critical": "#ef4444",
}
RISK_EMOJI = {
    "Safe": "✅", "Low": "🟡", "Medium": "🟠", "High": "🔴", "Critical": "🚨",
}

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 40px 20px 20px;">
    <div style="display:inline-block; background:rgba(0,229,255,0.08); border:1px solid rgba(0,229,255,0.25);
        border-radius:20px; padding:5px 16px; font-family:'Space Mono',monospace; font-size:11px;
        letter-spacing:2px; color:#00e5ff; text-transform:uppercase; margin-bottom:20px;">
        ⬤ &nbsp; v1.0 · PhishGuard
    </div>
    <div style="font-family:'Space Mono',monospace; font-size:40px; font-weight:700; color:#fff;
        letter-spacing:-1px; line-height:1.1;">
        Phishing <span style="color:#00e5ff">Detection</span><br>Tool
    </div>
    <div style="color:#64748b; font-size:15px; margin-top:12px; font-weight:300;">
        Analyse URLs and email content for phishing indicators
    </div>
</div>
<hr>
""", unsafe_allow_html=True)

# ── Input Card ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:#111520; border:1px solid #1e2535; border-radius:12px; padding:28px; margin-top:10px;">
    <div style="font-family:'Space Mono',monospace; font-size:11px; letter-spacing:2px;
        color:#64748b; text-transform:uppercase; margin-bottom:12px;">// Try an example</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
examples = {
    "safe":  "https://www.google.com/search?q=cybersecurity",
    "phish": "http://paypa1-secure-verify.tk/login?ref=account&update=true",
    "email": "From: security@paypa1-support.com\n\nDear Customer,\n\nWe have detected unusual activity on your account. Your account will be suspended within 24 hours unless you verify your account immediately.\n\nClick here: http://paypa1-verify.ml/secure-login\n\nFailure to act now will result in permanent account closure."
}

if col1.button("✅ Safe URL"):
    st.session_state.input_text = examples["safe"]
if col2.button("🎣 Phishing URL"):
    st.session_state.input_text = examples["phish"]
if col3.button("📧 Phishing Email"):
    st.session_state.input_text = examples["email"]

st.markdown("""
<div style="font-family:'Space Mono',monospace; font-size:11px; letter-spacing:2px;
    color:#64748b; text-transform:uppercase; margin:20px 0 8px;">// Input — URL or Email Body</div>
""", unsafe_allow_html=True)

input_text = st.text_area(
    label="input", label_visibility="collapsed",
    placeholder="Paste a URL (e.g. http://paypa1-secure.tk/login) or full email body here...",
    value=st.session_state.get("input_text", ""),
    height=140
)

analyse_btn = st.button("🔍  Analyse", type="primary", use_container_width=True)

# ── Result ────────────────────────────────────────────────────────────────────
if analyse_btn:
    if not input_text.strip():
        st.warning("Please paste a URL or email body first.")
    else:
        with st.spinner("Scanning for indicators..."):
            result = analyse(input_text.strip())

        color = RISK_COLORS[result.risk_level]
        emoji = RISK_EMOJI[result.risk_level]

        st.markdown("<hr>", unsafe_allow_html=True)

        # Score card
        st.markdown(f"""
        <div style="background:#111520; border:1px solid #1e2535; border-radius:12px; padding:28px; margin:20px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:20px;">
                <div>
                    <div style="font-family:'Space Mono',monospace; font-size:10px; letter-spacing:2px;
                        color:#64748b; text-transform:uppercase; margin-bottom:8px;">Risk Score</div>
                    <div style="font-family:'Space Mono',monospace; font-size:60px; font-weight:700;
                        line-height:1; color:{color};">
                        {result.risk_score}<span style="font-size:22px; color:#64748b;">/100</span>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-family:'Space Mono',monospace; font-size:10px; letter-spacing:2px;
                        color:#64748b; text-transform:uppercase; margin-bottom:8px;">Risk Level</div>
                    <div style="font-family:'Space Mono',monospace; font-size:18px; font-weight:700;
                        padding:10px 24px; border-radius:8px; border:2px solid {color}; color:{color}; display:inline-block;">
                        {emoji} {result.risk_level.upper()}
                    </div>
                </div>
            </div>
            <div style="margin-top:20px; background:#1e2535; border-radius:4px; height:6px; overflow:hidden;">
                <div style="width:{result.risk_score}%; height:100%; background:{color}; border-radius:4px;"></div>
            </div>
            <div style="margin-top:12px; font-family:'Space Mono',monospace; font-size:11px; color:#64748b;">
                TYPE: {result.input_type.upper()} &nbsp;·&nbsp; FLAGS: {len(result.flags)}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Flags
        st.markdown("""
        <div style="font-family:'Space Mono',monospace; font-size:11px; letter-spacing:2px;
            color:#64748b; text-transform:uppercase; margin:24px 0 12px;">// Indicators Detected</div>
        """, unsafe_allow_html=True)

        if result.flags:
            flags_html = ""
            for flag in result.flags:
                flags_html += f"""
                <div style="background:rgba(239,68,68,0.07); border:1px solid rgba(239,68,68,0.18);
                    border-radius:8px; padding:12px 16px; margin-bottom:8px; font-size:13px;
                    color:#fca5a5; display:flex; gap:10px;">
                    <span style="flex-shrink:0;">⚠</span><span>{flag}</span>
                </div>"""
            st.markdown(flags_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(34,197,94,0.08); border:1px solid rgba(34,197,94,0.2);
                border-radius:8px; padding:16px; font-size:14px; color:#86efac; text-align:center;">
                ✓ &nbsp; No suspicious indicators detected. This looks clean.
            </div>
            """, unsafe_allow_html=True)

        # Details
        if result.details:
            st.markdown("""
            <div style="font-family:'Space Mono',monospace; font-size:11px; letter-spacing:2px;
                color:#64748b; text-transform:uppercase; margin:24px 0 12px;">// Analysis Details</div>
            """, unsafe_allow_html=True)
            for key, val in result.details.items():
                display_val = ', '.join(val) if isinstance(val, list) else str(val)
                st.markdown(f"""
                <div style="background:#0a0c10; border:1px solid #1e2535; border-radius:6px;
                    padding:10px 14px; margin-bottom:8px;">
                    <div style="font-family:'Space Mono',monospace; font-size:10px; color:#64748b;
                        text-transform:uppercase; letter-spacing:1px;">{key.replace('_', ' ')}</div>
                    <div style="font-family:'Space Mono',monospace; font-size:12px; color:#e2e8f0;
                        margin-top:4px; word-break:break-all;">{display_val}</div>
                </div>
                """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; font-family:'Space Mono',monospace; font-size:10px;
    color:#64748b; letter-spacing:1px; padding-bottom:20px;">
    PHISHGUARD &nbsp;·&nbsp; PYTHON & STREAMLIT &nbsp;·&nbsp; FOR EDUCATIONAL PURPOSES
</div>
""", unsafe_allow_html=True)

import re
import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv
from utils.gmail_auth import authenticate_gmail
from tools.gmail_tools import get_unread_emails, get_email_content, send_message, mark_as_read
from tools.compose_tools import compose_email
from graph.graph_builder import build_graph

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Agentic Email Manager", page_icon="✉️", layout="wide")

# ── STYLES ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0d1117; }

/* ── Hero Banner ── */
.hero {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px 28px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.hero-title { font-size: 1.6em; font-weight: 700; color: #e6edf3; letter-spacing: -0.02em; }
.hero-sub   { font-size: 0.82em; color: #8b949e; margin-top: 2px; }
.hero-clock { text-align: right; }
.hero-time  { font-size: 1.8em; font-weight: 600; color: #58a6ff; font-variant-numeric: tabular-nums; }
.hero-date  { font-size: 0.78em; color: #8b949e; margin-top: 2px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }

/* ── Glassmorphism cards ── */
.glass {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 14px;
}

/* ── Email header (glass variant) ── */
.email-header {
    background: linear-gradient(135deg,rgba(31,41,55,0.9),rgba(17,24,39,0.9));
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 18px;
    line-height: 1.75;
}

/* ── Priority border stripes ── */
.priority-card {
    border-left: 4px solid;
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 6px;
    background: rgba(255,255,255,0.03);
}
.p-high   { border-color: #f87171; }
.p-medium { border-color: #fbbf24; }
.p-low    { border-color: #34d399; }
.p-none   { border-color: #374151; }

/* ── Sender row ── */
.sender-row { display:flex; align-items:center; gap:10px; padding:4px 0; }
.sender-avatar { width:28px; height:28px; border-radius:50%; object-fit:contain; background:#1f2937; flex-shrink:0; }
.sender-subject { font-size:0.84em; font-weight:600; color:#e6edf3; }
.sender-name    { font-size:0.72em; color:#8b949e; }

/* ── Badges ── */
.badge { display:inline-block; padding:3px 12px; border-radius:20px; font-size:0.75em; font-weight:600; }
.badge-work       { background:#1d4ed8; color:#fff; }
.badge-personal   { background:#065f46; color:#fff; }
.badge-spam       { background:#7f1d1d; color:#fff; }
.badge-newsletter { background:#4c1d95; color:#fff; }
.badge-unknown    { background:#374151; color:#fff; }

/* ── Sentiment badges ── */
.sentiment { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.75em; font-weight:600; margin-left:8px; }
.s-urgent   { background:rgba(248,113,113,0.2); color:#f87171; border:1px solid #f87171; }
.s-positive { background:rgba(52,211,153,0.2); color:#34d399; border:1px solid #34d399; }
.s-neutral  { background:rgba(139,148,158,0.2); color:#8b949e; border:1px solid #8b949e; }
.s-negative { background:rgba(251,191,36,0.2);  color:#fbbf24; border:1px solid #fbbf24; }
.s-curious  { background:rgba(88,166,255,0.2);  color:#58a6ff; border:1px solid #58a6ff; }

/* ── Priority text colors ── */
.priority-high   { color:#f87171; font-weight:600; }
.priority-medium { color:#fbbf24; font-weight:600; }
.priority-low    { color:#34d399; font-weight:600; }

/* ── Inputs ── */
div[data-testid="stTextArea"] textarea {
    background-color:#1c2333!important; color:#e6edf3!important;
    border:1px solid #30363d!important; border-radius:8px!important;
}
.stButton > button { border-radius:8px!important; font-weight:500!important; }
hr { border-color:#30363d!important; }
</style>
""", unsafe_allow_html=True)

# ── HERO BANNER ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div>
    <div class="hero-title">✉️ &nbsp;Agentic Email Manager</div>
    <div class="hero-sub">Powered by GPT-4o &amp; LangGraph</div>
  </div>
  <div class="hero-clock">
    <div class="hero-time" id="hero-time">--:--:--</div>
    <div class="hero-date" id="hero-date"></div>
  </div>
</div>
<script>
(function tick(){
  var n=new Date();
  var te=document.getElementById('hero-time');
  var de=document.getElementById('hero-date');
  if(te) te.textContent=n.toLocaleTimeString('en-US',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
  if(de) de.textContent=n.toLocaleDateString('en-US',{weekday:'long',month:'long',day:'numeric',year:'numeric'});
  setTimeout(tick,1000);
})();
</script>
""", unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def get_favicon(email_str):
    m = re.search(r'@([\w.\-]+)', email_str)
    return f"https://icons.duckduckgo.com/ip3/{m.group(1)}.ico" if m else ""

def display_name(sender):
    return sender.split("<")[0].strip().strip('"') if "<" in sender else sender

TONES = ["Professional", "Friendly", "Concise", "Assertive", "Casual"]
TONE_EMOJI = {"Professional":"👔","Friendly":"😊","Concise":"⚡","Assertive":"💪","Casual":"👋"}

SENTIMENT_META = {
    "Urgent":   ("🚨", "s-urgent"),
    "Positive": ("😊", "s-positive"),
    "Neutral":  ("😐", "s-neutral"),
    "Negative": ("😟", "s-negative"),
    "Curious":  ("🤔", "s-curious"),
}

PRIORITY_CLASS = {"High":"p-high","Medium":"p-medium","Low":"p-low"}

# ── SESSION STATE ─────────────────────────────────────────────────────────────
load_dotenv()

if "service" not in st.session_state:
    with st.spinner("Connecting to Gmail…"):
        st.session_state.service = authenticate_gmail()

for k, v in {"emails":[],"selected_email":None,"ai_results":None,
             "compose_result":None,"email_meta":{}}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# email_meta stores {id: {priority, classification, sentiment}} after agent runs

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📬 Inbox")
    if st.button("🔄 Refresh", use_container_width=True):
        with st.spinner("Fetching…"):
            st.session_state.emails = get_unread_emails(st.session_state.service, max_results=10)
            st.session_state.selected_email = None
            st.session_state.ai_results = None
    st.divider()

    # ── Analytics mini panel ─────────────────────────────────────────────────
    emails = st.session_state.emails
    meta   = st.session_state.email_meta

    total = len(emails)
    if total:
        st.markdown(f"<div style='color:#8b949e;font-size:0.8em;margin-bottom:6px'>"
                    f"<b style='color:#e6edf3'>{total}</b> unread emails</div>",
                    unsafe_allow_html=True)

        # Build stats from processed emails
        stats = {"Work":0,"Personal":0,"Newsletter":0,"Spam":0}
        for v in meta.values():
            c = v.get("classification","")
            if c in stats:
                stats[c] += 1

        processed = sum(stats.values())
        if processed:
            fig = go.Figure(go.Pie(
                labels=list(stats.keys()),
                values=list(stats.values()),
                hole=0.6,
                marker_colors=["#1d4ed8","#065f46","#4c1d95","#7f1d1d"],
                textinfo="none",
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=True,
                legend=dict(font=dict(color="#8b949e", size=11)),
                margin=dict(l=0,r=0,t=0,b=0),
                height=160,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

        st.divider()

    if not emails:
        st.caption("Click **Refresh** to load your inbox.")
    else:
        for em in emails:
            eid     = em["id"]
            subj    = em.get("subject","No Subject")
            sender  = em.get("sender","Unknown")
            favicon = get_favicon(sender)
            dname   = display_name(sender)
            short   = (subj[:34]+"…") if len(subj)>34 else subj

            # Priority stripe from processed meta (or none)
            p_cls = PRIORITY_CLASS.get(meta.get(eid,{}).get("priority",""), "p-none")

            avatar_html = (
                f'<img class="sender-avatar" src="{favicon}" onerror="this.style.display=\'none\'"/>'
                if favicon else '<span style="font-size:1.3em">🧑</span>'
            )
            st.markdown(f"""
            <div class="priority-card {p_cls}">
              <div class="sender-row">
                {avatar_html}
                <div>
                  <div class="sender-subject">{short}</div>
                  <div class="sender-name">{dname}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Open →", key=f"btn_{eid}", use_container_width=True):
                with st.spinner("Loading…"):
                    st.session_state.selected_email = get_email_content(st.session_state.service, eid)
                st.session_state.ai_results = None

# ── TABS ──────────────────────────────────────────────────────────────────────
tab_inbox, tab_compose = st.tabs(["📬 Inbox / Reply", "✍️ Compose New Email"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — INBOX
# ═══════════════════════════════════════════════════════════════════════════════
with tab_inbox:
    if not st.session_state.selected_email:
        st.info("👈 Select an email from the sidebar to get started.")
        st.stop()

    email = st.session_state.selected_email
    favicon = get_favicon(email["sender"])
    dname   = display_name(email["sender"])

    avatar_tag = (
        f'<img src="{favicon}" onerror="this.style.display=\'none\'" '
        f'style="width:40px;height:40px;border-radius:50%;object-fit:contain;background:#1f2937"/>'
        if favicon else '<span style="font-size:2em">🧑</span>'
    )

    # Show sentiment badge if already processed
    eid_meta = st.session_state.email_meta.get(email["id"], {})
    sent = eid_meta.get("sentiment","")
    s_emoji, s_cls = SENTIMENT_META.get(sent, ("",""))
    sentiment_html = (
        f"<span class='sentiment {s_cls}'>{s_emoji} {sent}</span>"
        if sent else ""
    )

    st.markdown(f"""
    <div class="email-header">
      <div style="display:flex;align-items:center;gap:14px;margin-bottom:10px">
        {avatar_tag}
        <div>
          <div style="font-size:1.05em;font-weight:600;color:#e6edf3">{dname}</div>
          <div style="font-size:0.8em;color:#8b949e">{email['sender']}</div>
        </div>
        {sentiment_html}
      </div>
      <hr/>
      <b>Subject:</b> {email['subject']}
    </div>
    """, unsafe_allow_html=True)

    col_orig, col_ai = st.columns([1,1], gap="large")

    with col_orig:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("### 📄 Original Email")
        body = email["body"] or email.get("snippet","(no body)")
        st.text_area("", value=body, height=360, disabled=True, label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_ai:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("### 🤖 AI Reply Workspace")

        tone = st.selectbox(
            "🎭 Reply Tone",
            options=TONES,
            format_func=lambda t: f"{TONE_EMOJI[t]}  {t}",
        )

        if st.button("▶️ Run AI Agent", type="primary", use_container_width=True):
            steps = st.empty()
            log   = []
            def show(msg):
                log.append(msg)
                steps.markdown("\n\n".join(log))

            with st.spinner("Running agent pipeline…"):
                try:
                    app = build_graph()
                    final = app.invoke({
                        "email_id":     email["id"],
                        "gmail_service": st.session_state.service,
                        "messages":     [],
                        "ui_mode":      True,
                        "tone":         tone,
                    })
                    st.session_state.ai_results = final
                    # Cache meta for sidebar colouring
                    st.session_state.email_meta[email["id"]] = {
                        "priority":       final.get("priority","Medium"),
                        "classification": final.get("classification","Work"),
                        "sentiment":      final.get("sentiment","Neutral"),
                    }
                except Exception as e:
                    st.error(f"Agent error: {e}")
            steps.empty()

        res = st.session_state.ai_results
        if res:
            classification = res.get("classification","Unknown")
            priority       = res.get("priority","Medium")
            sentiment      = res.get("sentiment","Neutral")
            summary        = res.get("summary")
            draft          = res.get("draft_response")

            b_cls  = f"badge-{classification.lower()}"
            p_col  = f"priority-{priority.lower()}"
            s_em, s_cl = SENTIMENT_META.get(sentiment, ("😐","s-neutral"))

            st.markdown(
                f"<span class='badge {b_cls}'>{classification}</span> &nbsp;"
                f"Priority: <span class='{p_col}'>{priority}</span> &nbsp;"
                f"<span class='sentiment {s_cl}'>{s_em} {sentiment}</span>",
                unsafe_allow_html=True
            )
            st.divider()

            if classification in ("Spam","Newsletter"):
                st.info("ℹ️ Classified as **Spam / Newsletter** — no reply generated.")
            else:
                if summary:
                    with st.expander("📝 AI Summary", expanded=True):
                        st.markdown(summary)
                else:
                    st.warning("No summary generated.")

                st.markdown(f"**✍️ Draft — {TONE_EMOJI.get(tone,'')} {tone}**")
                draft_text = st.text_area("", value=draft or "", height=200, label_visibility="collapsed")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("🚀 Send Reply", use_container_width=True,
                                 disabled=not bool(draft_text.strip())):
                        with st.spinner("Sending…"):
                            ok = send_message(
                                st.session_state.service,
                                to=email["sender"],
                                subject=f"Re: {email['subject']}",
                                body=draft_text,
                                thread_id=email["threadId"]
                            )
                        if ok:
                            st.success("✅ Sent!")
                            mark_as_read(st.session_state.service, email["id"])
                        else:
                            st.error("Send failed.")
                with c2:
                    if st.button("🗑️ Skip", use_container_width=True):
                        st.info("Skipped.")

            with st.expander("🔍 Debug — Raw State"):
                st.json({k:v for k,v in res.items() if k not in ("gmail_service","messages")})

        st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — COMPOSE
# ═══════════════════════════════════════════════════════════════════════════════
with tab_compose:
    st.markdown("# ✍️ Compose New Email")
    st.caption("Describe your intent — GPT-4o writes the full email.")
    st.divider()

    c_left, c_right = st.columns([1,1], gap="large")

    with c_left:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("### 📋 Details")
        to_addr = st.text_input("📧 Recipient", placeholder="someone@example.com")
        topic   = st.text_area("📝 Topic / Brief", height=110,
                                placeholder="e.g. Schedule a 30-min call for Thursday to discuss the proposal.")
        tone_c  = st.selectbox("🎭 Tone", TONES,
                                format_func=lambda t: f"{TONE_EMOJI[t]}  {t}", key="ctone")
        if st.button("🤖 Generate Draft", type="primary", use_container_width=True):
            if not to_addr.strip():
                st.error("Enter a recipient email.")
            elif not topic.strip():
                st.error("Describe the topic.")
            else:
                with st.spinner("Generating…"):
                    try:
                        st.session_state.compose_result = compose_email(to_addr, topic, tone_c)
                    except Exception as e:
                        st.error(f"Error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("### 👁️ Preview & Send")
        cr = st.session_state.compose_result
        if not cr:
            st.info("Fill details and click **Generate Draft**.")
        else:
            subj_e = st.text_input("Subject", value=cr.get("subject",""), key="csubj")
            body_e = st.text_area("Body", value=cr.get("body",""), height=300, key="cbody")
            cs1, cs2 = st.columns(2)
            with cs1:
                if st.button("🚀 Send", type="primary", use_container_width=True,
                             disabled=not to_addr.strip()):
                    with st.spinner("Sending…"):
                        ok = send_message(st.session_state.service, to_addr, subj_e, body_e)
                    if ok:
                        st.success(f"✅ Sent to {to_addr}!")
                        st.session_state.compose_result = None
                    else:
                        st.error("Failed.")
            with cs2:
                if st.button("🔄 Regenerate", use_container_width=True):
                    with st.spinner("Regenerating…"):
                        try:
                            st.session_state.compose_result = compose_email(to_addr, topic, tone_c)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

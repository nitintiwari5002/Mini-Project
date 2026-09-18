import streamlit as st
import streamlit.components.v1 as components
import base64
import pickle
import uuid
from pathlib import Path
from fpdf import FPDF
from core.db import create_tables, register_user, login_user
from core.ai import prompt
from components.navbar import render_navbar
st.set_page_config(page_title="InterviewAce", page_icon="", layout="wide")
render_navbar("home")
# -----------------------------
# APP INITIALIZATION
# -----------------------------
create_tables()

# ---------------------------------------------------------
# PERSISTENT INTERVIEW STATE
# ---------------------------------------------------------
# Streamlit session_state is reset when the browser is refreshed.
# We therefore keep the active user's interview state on disk and
# restore it using a random browser session token stored in the URL.
# This also keeps questions/answers separate between users.
STATE_FILE = Path(__file__).resolve().parent / "interview_state.pkl"

SESSION_DEFAULTS = {
    "navbar_state": None,
    "role": None,
    "login_success": None,
    "username": None,
    "auth_token": None,
    "questions_generated": None,
    "qa_pairs": None,
    "analysis": None,
    "score": None,
    "current_question": 0,
    "interview_started": False,
    "interview_config": None,
}

def load_persistent_store():
    if not STATE_FILE.exists():
        return {"sessions": {}, "interviews": {}}
    try:
        with STATE_FILE.open("rb") as f:
            data = pickle.load(f)
        if not isinstance(data, dict):
            return {"sessions": {}, "interviews": {}}
        data.setdefault("sessions", {})
        data.setdefault("interviews", {})
        return data
    except Exception:
        return {"sessions": {}, "interviews": {}}

def save_persistent_store(data):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_file = STATE_FILE.with_suffix(".tmp")
    with temp_file.open("wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    temp_file.replace(STATE_FILE)

def init_session():
    for key, value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_auth_token_from_url():
    try:
        return st.query_params.get("session")
    except Exception:
        return None

def restore_persistent_session():
    token = get_auth_token_from_url()
    if not token:
        return

    store = load_persistent_store()
    session = store.get("sessions", {}).get(token)
    if not session:
        return

    username = session.get("username")
    if not username:
        return

    st.session_state.auth_token = token
    st.session_state.username = username
    st.session_state.navbar_state = "user_dashboard"

    saved = store.get("interviews", {}).get(username)
    if saved:
        for key in (
            "questions_generated",
            "qa_pairs",
            "analysis",
            "score",
            "current_question",
            "interview_started",
            "interview_config",
        ):
            if key in saved:
                st.session_state[key] = saved[key]

def persist_interview_state():
    username = st.session_state.get("username")
    if not username:
        return

    store = load_persistent_store()
    store.setdefault("interviews", {})
    store["interviews"][username] = {
        "questions_generated": st.session_state.get("questions_generated"),
        "qa_pairs": st.session_state.get("qa_pairs"),
        "analysis": st.session_state.get("analysis"),
        "score": st.session_state.get("score"),
        "current_question": st.session_state.get("current_question", 0),
        "interview_started": st.session_state.get("interview_started", False),
        "interview_config": st.session_state.get("interview_config"),
    }
    save_persistent_store(store)

def create_login_session(username):
    token = uuid.uuid4().hex
    store = load_persistent_store()
    store.setdefault("sessions", {})
    store["sessions"][token] = {"username": username}
    save_persistent_store(store)
    st.session_state.auth_token = token
    st.session_state.username = username
    st.query_params["session"] = token

def reset_to_home():
    # Do not delete the saved interview. It remains available on next login.
    for key, value in SESSION_DEFAULTS.items():
        st.session_state[key] = value
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.rerun()

init_session()
restore_persistent_session()

# -----------------------------
# HELPERS
# -----------------------------
def img_to_data_url(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    data = p.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    mime = "image/jpeg" if p.suffix.lower() in [".jpg", ".jpeg"] else "image/png"
    return f"data:{mime};base64,{b64}"

def sanitize_for_pdf(text: str) -> str:
    replacements = {
        "–": "-", "—": "-", "“": '"', "”": '"', "’": "'",
        "•": "-", "→": "->", "←": "<-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return "".join(ch if ord(ch) <= 255 else "?" for ch in text)

def create_interview_pdf(text: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=11)
    for line in sanitize_for_pdf(text).splitlines():
        pdf.multi_cell(0, 7, line)
    return pdf.output(dest="S").encode("latin-1", "ignore")

def compute_score_from_analysis(analysis: str) -> int:
    if not isinstance(analysis, str) or not analysis.strip():
        return 0
    text = analysis.lower()
    score = 50
    positive = ["strong", "excellent", "good", "confident", "clear", "impressive", "well-structured", "outstanding", "solid"]
    negative = ["weak", "improve", "improvement", "poor", "unclear", "lack", "insufficient", "disorganized", "inconsistent"]
    score += sum(5 for word in positive if word in text)
    score -= sum(5 for word in negative if word in text)
    return max(0, min(100, score))

def get_score_breakdown(analysis: str) -> dict:
    text = (analysis or "").lower()
    return {
        "Strengths": 70 if any(x in text for x in ["strength", "strong", "good"]) else 40,
        "Weaknesses": 60 if any(x in text for x in ["weak", "improve", "lack"]) else 40,
        "Communication": 65 if any(x in text for x in ["communication", "clarity", "clear"]) else 40,
        "Technical Depth": 65 if any(x in text for x in ["technical", "concepts", "knowledge"]) else 40,
    }

# -----------------------------
# GLOBAL CLASSY THEME
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

:root {
    --ink: #172033;
    --muted: #667085;
    --cream: #f7f5f0;
    --paper: #ffffff;
    --navy: #182338;
    --gold: #c9a45c;
    --gold-light: #ead8ad;
    --line: #e7e2d8;
    --shadow: 0 18px 55px rgba(24,35,56,.10);
}

html, body, [class*="css"] {
    font-family: "DM Sans", sans-serif;
    color: var(--ink);
}
.stApp {
    background:
        radial-gradient(circle at 8% 0%, rgba(201,164,92,.12), transparent 26%),
        radial-gradient(circle at 92% 12%, rgba(24,35,56,.08), transparent 25%),
        linear-gradient(180deg, #fbfaf7 0%, #f3f1eb 100%);
}
.block-container {
    max-width: 1240px;
    padding-top: 1.2rem;
    padding-bottom: 4rem;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { visibility: hidden; }

.topbar {
    padding: 1.05rem 1.4rem;
    border: 1px solid rgba(255,255,255,.7);
    border-radius: 20px;
    background: rgba(24,35,56,.96);
    box-shadow: 0 14px 35px rgba(24,35,56,.16);
    display:flex;
    align-items:left;
    justify-content:space-between;
    color:#fff;
    margin-bottom: 1.6rem;
}
.brand { font-weight:700; letter-spacing:.04em; font-size:1.15rem; }
.brand span { color:var(--gold-light); }
.eyebrow {
    text-transform:uppercase;
    letter-spacing:.18em;
    font-size:.72rem;
    font-weight:700;
    color:var(--gold);
}
.hero {
    padding: 3.8rem 2rem 3.2rem;
    border-radius: 30px;
    background:
        linear-gradient(135deg, rgba(24,35,56,.98), rgba(34,47,72,.96)),
        radial-gradient(circle at 80% 20%, rgba(201,164,92,.25), transparent 35%);
    color:#fff;
    box-shadow: var(--shadow);
    text-align:center;
    overflow:hidden;
    position:relative;
}
.hero:after {
    content:"";
    position:absolute;
    width:220px;height:220px;
    right:-70px;top:-70px;
    border:1px solid rgba(234,216,173,.35);
    border-radius:50%;
}
.hero h1 {
    font-family:"Playfair Display",serif;
    font-size:clamp(2.5rem,6vw,4.6rem);
    line-height:1.05;
    margin:.45rem 0 1rem;
    color:#fff;
}
.hero p { max-width:720px; margin:auto; color:#e9edf4; font-size:1.08rem; line-height:1.7; }

.card {
    background:rgba(255,255,255,.88);
    border:1px solid rgba(231,226,216,.9);
    border-radius:24px;
    padding:1.7rem;
    box-shadow:0 12px 35px rgba(24,35,56,.07);
}
.section-title {
    font-family:"Playfair Display",serif;
    font-size:1.65rem;
    color:var(--navy);
    margin:0 0 .45rem;
}
.muted { color:var(--muted); line-height:1.7; }
.badge {
    display:inline-block;
    padding:.45rem .8rem;
    margin:.25rem;
    border:1px solid #e6d8b9;
    border-radius:999px;
    background:#fbf7ed;
    color:#6e5730;
    font-size:.82rem;
    font-weight:600;
}
.feature-strip {
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:1rem;
    margin:1.4rem 0;
}
.feature-mini {
    background:#fff;
    border:1px solid var(--line);
    border-radius:20px;
    padding:1.25rem;
    box-shadow:0 10px 30px rgba(24,35,56,.06);
}
.feature-mini strong { display:block; margin-bottom:.35rem; color:var(--navy); }
.feature-mini span { color:var(--muted); font-size:.9rem; line-height:1.5; }

.stButton > button, .stDownloadButton > button {
    border-radius:12px !important;
    min-height:44px;
    font-weight:700 !important;
    border:1px solid #c9a45c !important;
    background:linear-gradient(135deg,#c9a45c,#dfc485) !important;
    color:#182338 !important;
    box-shadow:0 8px 22px rgba(201,164,92,.18) !important;
    transition:transform .2s ease, box-shadow .2s ease !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform:translateY(-2px);
    box-shadow:0 12px 28px rgba(201,164,92,.28) !important;
}
input, textarea, [data-baseweb="select"] > div {
    border-radius:12px !important;
}
[data-testid="stMetric"] {
    background:#fff;
    border:1px solid var(--line);
    border-radius:18px;
    padding:1rem;
}
hr { border-color:var(--line) !important; }
[data-testid="stAlert"] p { color: #000000 !important; }
@media (max-width: 800px) {
    .feature-strip { grid-template-columns:1fr; }
    .hero { padding:2.7rem 1rem; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="topbar">
  <div class="brand">Interview<span>Ace</span></div>
  <div class="eyebrow">AI Interview Studio</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# WELCOME
# -----------------------------
def render_welcome():
    st.markdown("""
    <section class="hero">
        <div class="eyebrow">Prepare smarter · perform better</div>
        <h1>Own Your Next Interview.</h1>
        <p>Practice AI-powered mock interviews, receive focused feedback, and build the confidence to walk into your next interview prepared.</p>
    </section>
    """, unsafe_allow_html=True)

    img_paths = ["assets/banner1.png", "assets/banner2.png", "assets/banner3.png"]
    images = [img_to_data_url(p) for p in img_paths]

    if all(images):
        carousel_html = f"""
        <div id="ia-carousel" style="margin:28px auto 30px;max-width:1100px;position:relative;overflow:hidden;border-radius:26px;box-shadow:0 24px 60px rgba(24,35,56,.18);background:#182338;">
          <div id="ia-slides" style="display:flex;width:300%;transition:transform .55s cubic-bezier(.2,.7,.2,1);">
            <img src="{images[0]}" style="width:33.3333%;height:390px;object-fit:cover;flex-shrink:0;" alt="Interview practice">
            <img src="{images[1]}" style="width:33.3333%;height:390px;object-fit:cover;flex-shrink:0;" alt="AI feedback">
            <img src="{images[2]}" style="width:33.3333%;height:390px;object-fit:cover;flex-shrink:0;" alt="Interview analytics">
          </div>
          <button id="ia-prev" style="position:absolute;left:18px;top:50%;transform:translateY(-50%);width:46px;height:46px;border:0;border-radius:50%;background:rgba(24,35,56,.78);color:#fff;font-size:20px;cursor:pointer;">‹</button>
          <button id="ia-next" style="position:absolute;right:18px;top:50%;transform:translateY(-50%);width:46px;height:46px;border:0;border-radius:50%;background:rgba(24,35,56,.78);color:#fff;font-size:20px;cursor:pointer;">›</button>
          <div id="ia-dots" style="position:absolute;bottom:16px;left:50%;transform:translateX(-50%);display:flex;gap:8px;">
            <span data-i="0" style="width:9px;height:9px;border-radius:50%;background:#fff;cursor:pointer;"></span>
            <span data-i="1" style="width:9px;height:9px;border-radius:50%;background:rgba(255,255,255,.45);cursor:pointer;"></span>
            <span data-i="2" style="width:9px;height:9px;border-radius:50%;background:rgba(255,255,255,.45);cursor:pointer;"></span>
          </div>
        </div>
        <script>
        (() => {{
          const root = document.getElementById("ia-carousel");
          const slides = document.getElementById("ia-slides");
          const prev = document.getElementById("ia-prev");
          const next = document.getElementById("ia-next");
          const dots = root ? root.querySelectorAll("#ia-dots span") : [];
          let index = 0, timer;

          function update() {{
            if (!slides) return;
            slides.style.transform = `translateX(-${{index * 33.3333}}%)`;
            dots.forEach((d,i) => d.style.background = i === index ? "#fff" : "rgba(255,255,255,.45)");
          }}
          function go(delta) {{
            index = (index + delta + 3) % 3;
            update();
          }}
          if (prev) prev.addEventListener("click", () => go(-1));
          if (next) next.addEventListener("click", () => go(1));
          dots.forEach(d => d.addEventListener("click", () => {{
            index = Number(d.dataset.i); update();
          }}));
          function start() {{ timer = setInterval(() => go(1), 4000); }}
          function stop() {{ clearInterval(timer); }}
          root.addEventListener("mouseenter", stop);
          root.addEventListener("mouseleave", start);
          update(); start();
        }})();
        </script>
        """
        components.html(carousel_html, height=450, scrolling=False)

    st.markdown("""
    <div class="feature-strip">
      <div class="feature-mini"><strong>01 · Adaptive Questions</strong><span>Generate questions around your career field, interview type, difficulty, role, and custom focus.</span></div>
      <div class="feature-mini"><strong>02 · Practice Naturally</strong><span>Use audio responses to simulate a realistic interview environment.</span></div>
      <div class="feature-mini"><strong>03 · Actionable Feedback</strong><span>Review an AI-generated evaluation and download a polished interview report.</span></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        pass
    with c2:
        a, b = st.columns(2)
        with a:
            if st.button("Login", use_container_width=True):
                st.session_state.navbar_state = "login"
                st.rerun()
        with b:
            if st.button("Register", use_container_width=True):
                st.session_state.navbar_state = "register"
                st.rerun()

# -----------------------------
# LOGIN / REGISTER
# -----------------------------
def render_login():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">Welcome back</div><div class="section-title">Sign in to InterviewAce</div><p class="muted">Continue your interview preparation journey.</p>', unsafe_allow_html=True)
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Login", use_container_width=True):
            if login_user(u, p):
                create_login_session(u)
                st.session_state.navbar_state = "user_dashboard"
                st.rerun()
            else:
                st.error("Invalid credentials.")
    with c2:
        if st.button("Back", use_container_width=True):
            reset_to_home()
    st.markdown('</div>', unsafe_allow_html=True)

def render_register():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">Create your account</div><div class="section-title">Start preparing with InterviewAce</div><p class="muted">Create an account to access your personalized interview workspace.</p>', unsafe_allow_html=True)
    u = st.text_input("Username")
    e = st.text_input("Email")
    p = st.text_input("Password", type="password")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Create Account", use_container_width=True):
            try:
                register_user(u, e, p)
                st.success("Registered successfully. You can now log in.")
            except Exception as exc:
                st.error(f"Registration failed: {exc}")
    with c2:
        if st.button("Back", use_container_width=True):
            reset_to_home()
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# USER DASHBOARD
# -----------------------------
def render_user_dashboard():
    st.markdown("""
    <div class="hero" style="text-align:left;padding:2.2rem 2rem;">
      <div class="eyebrow">Interview workspace</div>
      <h1 style="font-size:2.6rem;margin-bottom:.6rem;">Your Mock Interview</h1>
      <p style="margin:0;max-width:720px;">Set your interview parameters, generate tailored questions, record answers, and receive a focused performance review.</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Interview Setup</div>', unsafe_allow_html=True)

        saved_config = st.session_state.get("interview_config") or {}

        if st.session_state.get("qa_pairs") and st.session_state.get("interview_started"):
            current = st.session_state.get("current_question", 0) + 1
            total = len(st.session_state.get("qa_pairs") or [])
            st.info(
                f"Interview in progress — question {current} of {total}. "
                "Refreshing the page will not reset your interview."
            )


        career_options = [
            "Software Engineering", "Data Structures", "Data Science",
            "Machine Learning", "Cyber Security", "Cloud Computing",
            "Database Administrator", "Data Analyst", "Web Development",
        ]
        interview_type_options = ["HR", "Technical", "Behavioral"]
        difficulty_options = ["Basic", "Intermediate", "Advanced"]

        saved_career = saved_config.get("career", career_options[0])
        saved_type = saved_config.get("interview_type", interview_type_options[0])
        saved_difficulty = saved_config.get("difficulty", difficulty_options[0])
        saved_num_q = max(3, min(10, int(saved_config.get("num_q", 5))))

        career = st.selectbox(
            "Career Field",
            career_options,
            index=career_options.index(saved_career) if saved_career in career_options else 0,
            key="career_field",
        )
        interview_type = st.selectbox(
            "Interview Type",
            interview_type_options,
            index=interview_type_options.index(saved_type) if saved_type in interview_type_options else 0,
            key="interview_type",
        )
        difficulty = st.selectbox(
            "Difficulty Level",
            difficulty_options,
            index=difficulty_options.index(saved_difficulty) if saved_difficulty in difficulty_options else 0,
            key="difficulty_level",
        )
        job_role = st.text_input(
            "Target role / position (optional)",
            value=saved_config.get("job_role", ""),
            placeholder="e.g. Backend Engineer",
            key="job_role",
        )
        custom_focus = st.text_area(
            "Custom focus (optional)",
            value=saved_config.get("custom_focus", ""),
            placeholder="e.g. system design, REST APIs, database transactions",
            key="custom_focus",
        )
        num_q = st.slider(
            "Number of questions", 3, 10, saved_num_q, key="num_questions"
        )

        if st.button("Start Interview", key="btn_start_interview", use_container_width=True):
            question_prompt = f"""
You are an experienced interviewer for {career} candidates.

Generate exactly {num_q} {interview_type} interview questions.

Target role/position: {job_role or "Not specified"}
Difficulty: {difficulty}
Additional focus: {custom_focus or "None"}

If Basic, focus on fundamentals and simple direct questions.
If Intermediate, focus on applied concepts and moderate depth.
If Advanced, focus on complex scenario-based and deep questions.

For each question:
- Write the question on one line starting with "Q:".
- On the next line write a short expected answer starting with "Expected answer:".
- Do not add numbering, bullets, or extra text.

Now generate {num_q} Q/A pairs.
"""
            raw, err = prompt(question_prompt, mode="questions")
            if err:
                st.error(err)
                return
            if not isinstance(raw, str) or not raw.strip():
                st.error("Could not generate questions. Please try again.")
                return

            qa_pairs = []
            lines = [line.strip() for line in raw.splitlines() if line.strip()]
            i = 0
            while i < len(lines):
                if lines[i].startswith("Q:"):
                    q = lines[i].split(":", 1)[1].strip()
                    expected = ""
                    if i + 1 < len(lines) and lines[i + 1].startswith("Expected answer:"):
                        expected = lines[i + 1].split(":", 1)[1].strip()
                        i += 1
                    qa_pairs.append({"question": q, "expected_answer": expected, "audio_bytes": None})
                i += 1

            qa_pairs = qa_pairs[:num_q]
            if len(qa_pairs) < num_q:
                st.error("The AI did not return enough valid questions. Please retry.")
                return

            st.session_state.qa_pairs = qa_pairs
            st.session_state.questions_generated = [p["question"] for p in qa_pairs]
            st.session_state.current_question = 0
            st.session_state.interview_started = True
            st.session_state.analysis = None
            st.session_state.score = None
            st.session_state.interview_config = {
                "career": career,
                "interview_type": interview_type,
                "difficulty": difficulty,
                "job_role": job_role,
                "custom_focus": custom_focus,
                "num_q": num_q,
            }
            persist_interview_state()
            st.success(f"{len(qa_pairs)} questions generated. Your interview has started.")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Camera Preview</div>', unsafe_allow_html=True)
        cam = st.camera_input("Camera Preview", key="single_camera")
        if cam:
            st.image(cam, use_container_width=True)
        else:
            st.markdown('<p class="muted">Camera preview is optional. Your interview can still be completed using audio responses.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    qa_pairs = st.session_state.get("qa_pairs") or []

    if qa_pairs and st.session_state.get("interview_started"):
        st.write("")
        st.markdown('<div class="section-title">Live Interview</div>', unsafe_allow_html=True)

        current_index = int(st.session_state.get("current_question", 0))
        current_index = max(0, min(current_index, len(qa_pairs) - 1))
        st.session_state.current_question = current_index
        pair = qa_pairs[current_index]

        st.progress((current_index + 1) / len(qa_pairs))

        st.markdown(
            f"""<div class="card" style="margin-bottom:18px;">
                <div class="eyebrow">Question {current_index + 1} of {len(qa_pairs)}</div>
                <div style="font-size:1.35rem;font-weight:700;color:#182338;line-height:1.6;margin-top:12px;">
                    {pair["question"]}
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

        # Expected answers are intentionally NEVER rendered in the interview UI.
        existing_audio = pair.get("audio_bytes")
        if existing_audio:
            st.success("Your recorded answer is saved. You can re-record it below if needed.")
            st.audio(existing_audio, format="audio/wav")

        audio = st.audio_input(
        "Record your answer",
        key=f"audio_{current_index}",
    )

        if audio:
            audio_bytes = audio.getvalue()

            if audio_bytes:
                pair["audio_bytes"] = audio_bytes
                persist_interview_state()

                st.audio(audio_bytes, format="audio/wav")
                st.success("Answer saved. You can continue to the next question.")

        nav_left, nav_right = st.columns([1, 1])

        with nav_left:
            if current_index > 0:
                if st.button(
                    "← Previous Question",
                    key=f"previous_{current_index}",
                    use_container_width=True,
                ):
                    st.session_state.current_question -= 1
                    persist_interview_state()
                    st.rerun()

        with nav_right:
            if current_index < len(qa_pairs) - 1:
                if st.button(
                    "Next Question →",
                    key=f"next_{current_index}",
                    use_container_width=True,
                ):
                    if not pair.get("audio_bytes"):
                        st.warning("Please record your answer before continuing.")
                    else:
                        st.session_state.current_question += 1
                        persist_interview_state()
                        st.rerun()
            else:
                if st.button(
                    "Submit Interview & Analyze",
                    key="btn_analyze",
                    use_container_width=True,
                ):
                    # # Save the latest recording before validating/submitting.
                    # if audio:
                    #     pair["audio_bytes"] = audio.read()

                    # Validate that the current question has an answer.
                    if not pair.get("audio_bytes"):
                        st.warning("Please record your answer before submitting.")

                    # Validate that every interview question has an answer.
                    elif not all(item.get("audio_bytes") for item in qa_pairs):
                        answered = sum(
                            1 for item in qa_pairs if item.get("audio_bytes")
                        )
                        st.warning(
                            f"Please answer every question before submitting. "
                            f"{answered}/{len(qa_pairs)} completed."
                        )

                    else:
                        # Persist the completed interview before starting analysis.
                        persist_interview_state()

                        qa_summary = []
                        for idx, item in enumerate(qa_pairs, 1):
                            qa_summary.append(
                                f"Q{idx}: {item['question']}\n"
                                f"Expected answer: {item.get('expected_answer', '')}\n"
                                "Candidate answer: provided"
                            )

                        analysis_prompt = f"""
                        You are an expert interviewer evaluating an audio-only mock interview.

                        Career Field: {career}
                        Interview Type: {interview_type}
                        Difficulty Level: {difficulty}
                        Target Role: {job_role or "Not specified"}
                        Custom Focus: {custom_focus or "None"}

                        Questions and answer availability:
                        {chr(10).join(qa_summary)}

                        The application has recorded an audio answer for every question, but no
                        audio transcript is available to you. Do not invent what the candidate said.
                        Evaluate the interview honestly using the question difficulty, expected
                        answers, interview context, and the fact that every question was attempted.

                        Use this format:
                        Strengths:
                        - ...

                        Weaknesses:
                        - ...

                        Improvement tips:
                        - ...

                        Use explicit words such as strong, excellent, good, weak, poor, unclear,
                        or lacking where appropriate.
"""

                        with st.spinner("Analyzing your interview..."):
                            analysis, err = prompt(
                                analysis_prompt,
                                mode="analysis",
                            )

                        if err:
                            st.error(f"Analysis failed: {err}")
                        elif not isinstance(analysis, str) or not analysis.strip():
                            st.error(
                                "The AI returned an empty analysis. "
                                "Please try submitting again."
                            )
                        else:
                            score = compute_score_from_analysis(analysis)
                            st.session_state.analysis = analysis
                            st.session_state.score = score
                            st.session_state.interview_started = False
                            persist_interview_state()
                            st.success("Interview completed successfully!")
                            st.rerun()

        # Persist the state on normal reruns too.
        persist_interview_state()

    if st.session_state.get("analysis"):
        st.write("")
        st.markdown('<div class="section-title">Performance Review</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Overall Score", f'{st.session_state.score}/100')
            st.progress(st.session_state.score / 100)
        with c2:
            breakdown = get_score_breakdown(st.session_state.analysis)
            bcols = st.columns(4)
            for idx, (label, value) in enumerate(breakdown.items()):
                with bcols[idx]:
                    st.metric(label, value)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(st.session_state.analysis)
        st.markdown('</div>', unsafe_allow_html=True)

        pdf_lines = [
            "InterviewAce - Interview Report",
            "=" * 42,
            "",
            f"Overall Score: {st.session_state.score}/100",
            "",
            st.session_state.analysis,
        ]
        pdf = create_interview_pdf("\n".join(pdf_lines))
        st.download_button("Download Interview Report (PDF)", pdf, "interview_report.pdf", "application/pdf")

    if st.button("Logout", key="logout_bottom"):
        reset_to_home()

# -----------------------------
# ROUTER
# -----------------------------
state = st.session_state.navbar_state
if state is None:
    render_welcome()
elif state == "login":
    render_login()
elif state == "register":
    render_register()
elif state == "user_dashboard":
    render_user_dashboard()
else:
    reset_to_home()

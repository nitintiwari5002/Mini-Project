import streamlit as st
from components.navbar import render_navbar
st.set_page_config(page_title="Features - InterviewAce", page_icon="✨", layout="wide")
render_navbar("home")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

:root {
    --navy:#182338;
    --gold:#c9a45c;
    --cream:#f7f5f0;
    --paper:#fff;
    --muted:#667085;
    --line:#e7e2d8;
}
html, body, [class*="css"] { font-family:"DM Sans",sans-serif; }
.stApp {
    background:
      radial-gradient(circle at 10% 0%, rgba(201,164,92,.14), transparent 28%),
      radial-gradient(circle at 90% 10%, rgba(24,35,56,.08), transparent 25%),
      linear-gradient(180deg,#fbfaf7,#f2f0e9);
}
.block-container { max-width:1200px; padding-top:1.2rem; padding-bottom:4rem; }
.topbar {
    background:rgba(24,35,56,.97); color:#fff; padding:1.05rem 1.4rem;
    border-radius:20px; display:flex; justify-content:space-between; align-items:center;
    box-shadow:0 14px 35px rgba(24,35,56,.15); margin-bottom:2rem;
}
.brand {font-size:1.15rem;font-weight:700;letter-spacing:.04em}
.brand span{color:#ead8ad}
.eyebrow{text-transform:uppercase;letter-spacing:.18em;font-size:.72rem;font-weight:700;color:#c9a45c}
.hero{
    text-align:center;padding:4rem 1.5rem;border-radius:30px;
    background:linear-gradient(135deg,#182338,#2b3955);
    color:#fff;box-shadow:0 22px 60px rgba(24,35,56,.16);margin-bottom:1.6rem;
}
.hero h1{font-family:"Playfair Display",serif;font-size:clamp(2.5rem,6vw,4.5rem);margin:.45rem 0 .8rem}
.hero p{max-width:760px;margin:auto;color:#e9edf4;font-size:1.05rem;line-height:1.7}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem}
.feature{
    background:rgba(255,255,255,.9);border:1px solid var(--line);border-radius:24px;
    padding:1.7rem;min-height:170px;box-shadow:0 12px 35px rgba(24,35,56,.07);
    transition:.25s ease;position:relative;overflow:hidden;
}
.feature:before{content:"";position:absolute;left:0;top:0;width:5px;height:100%;background:#c9a45c}
.feature:hover{transform:translateY(-5px);box-shadow:0 20px 45px rgba(24,35,56,.12)}
.icon{font-size:1.6rem;margin-bottom:.7rem}
.feature h3{margin:0 0 .45rem;color:#182338}
.feature p{margin:0;color:#667085;line-height:1.65}
.panel{background:#fff;border:1px solid var(--line);border-radius:24px;padding:1.8rem;margin-top:1.4rem;box-shadow:0 12px 35px rgba(24,35,56,.06)}
.panel h2{font-family:"Playfair Display",serif;color:#182338}
.panel li{margin:.55rem 0;color:#667085}
@media(max-width:800px){.grid{grid-template-columns:1fr}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="topbar">
  <div class="brand">Interview<span>Ace</span></div>
  <div class="eyebrow">Platform Features</div>
</div>
<div class="hero">
  <div class="eyebrow">Everything in one place</div>
  <h1>Everything You Need to Succeed</h1>
  <p>A refined AI-powered interview preparation workspace built to help candidates practice, understand their performance, and improve with purpose.</p>
</div>
""", unsafe_allow_html=True)

try:
    st.image("assets/Mini (2).png", width=220)
except Exception:
    pass

st.markdown('<h2 style="font-family:Playfair Display,serif;color:#182338;margin-top:1.5rem;">Core capabilities</h2>', unsafe_allow_html=True)

features = [
    ("🤖", "AI-powered Interviews", "Practice with intelligent, adaptive mock interviews and detailed feedback."),
    ("📊", "Real-time Analytics", "Track your performance and pinpoint areas for improvement instantly."),
    ("🏢", "Company Questions Generator", "Companies can generate role-specific interview questions and save preparation time."),
    ("💡", "AI Feedback", "Receive customized AI feedback based on the interview and identify areas to improve."),
    ("📄", "Resume Builder via AI", "Create professional resumes with AI assistance to highlight your strengths effectively."),
    ("🔎", "Resume Checker", "Analyze and improve your resume with AI-driven insights."),
]
cards = "".join(f"""
<div class="feature">
  <div class="icon">{icon}</div>
  <h3>{title}</h3>
  <p>{description}</p>
</div>
""" for icon, title, description in features)

st.markdown(f'<div class="grid">{cards}</div>', unsafe_allow_html=True)

st.markdown("""
<div class="panel">
<h2>For Candidates</h2>
<ul>
<li>AI-generated interview questions tailored to role and level.</li>
<li>Answer boxes for each question with detailed AI feedback.</li>
<li>Overall score and category-wise breakdown: strengths, weaknesses, communication, and technical depth.</li>
<li>Downloadable PDF report of your analysis.</li>
</ul>
</div>
<div class="panel">
<h2>For Companies</h2>
<ul>
<li>Generate consistent interview question sets for specific roles.</li>
<li>Quickly evaluate candidate responses with AI suggestions.</li>
<li>Use scores and analysis to guide hiring decisions.</li>
</ul>
</div>
<div class="panel">
<h2>Technology Stack</h2>
<ul>
<li>Streamlit for fast, interactive UI.</li>
<li>SQLite for lightweight authentication and data.</li>
<li>Groq / Qwen3 32B for AI generation and analysis.</li>
</ul>
</div>
""", unsafe_allow_html=True)

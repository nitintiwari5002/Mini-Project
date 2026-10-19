import streamlit as st
from components.navbar import render_navbar
st.set_page_config(page_title="About - InterviewAce", page_icon="◈", layout="wide")
render_navbar("home")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

html,body,[class*="css"]{font-family:"DM Sans",sans-serif}
.stApp{
 background:
 radial-gradient(circle at 10% 0%,rgba(201,164,92,.14),transparent 28%),
 radial-gradient(circle at 90% 10%,rgba(24,35,56,.08),transparent 25%),
 linear-gradient(180deg,#fbfaf7,#f1efe8);
}
.block-container{max-width:1200px;padding-top:1.2rem;padding-bottom:4rem}
.topbar{
 background:#182338;color:#fff;border-radius:20px;padding:1.05rem 1.4rem;
 display:flex;align-items:center;justify-content:space-between;box-shadow:0 14px 35px rgba(24,35,56,.15);
}
.brand{font-weight:700;font-size:1.15rem;letter-spacing:.04em}.brand span{color:#ead8ad}
.eyebrow{text-transform:uppercase;letter-spacing:.18em;font-size:.72rem;font-weight:700;color:#c9a45c}
.hero{
 margin-top:1.5rem;padding:4.5rem 1.5rem;text-align:center;border-radius:30px;
 background:linear-gradient(135deg,#182338,#2c3955);color:#fff;box-shadow:0 22px 60px rgba(24,35,56,.16);
}
.hero h1{font-family:"Playfair Display",serif;font-size:clamp(2.5rem,6vw,4.6rem);line-height:1.05;margin:.5rem 0 1rem}
.hero p{font-size:1.08rem;color:#e8ecf2;margin:auto;max-width:760px;line-height:1.7}
.card{
 background:rgba(255,255,255,.92);border:1px solid #e7e2d8;border-radius:24px;padding:2rem;
 box-shadow:0 14px 38px rgba(24,35,56,.07);height:100%;
}
.card h2{font-family:"Playfair Display",serif;color:#182338;margin-top:0}
.card p{color:#667085;line-height:1.8}
.badges{display:flex;flex-wrap:wrap;gap:.55rem;margin-top:1.3rem}
.badge{padding:.48rem .8rem;border-radius:999px;background:#fbf7ed;border:1px solid #ead8b0;color:#6e5730;font-size:.82rem;font-weight:600}
.vision{
 margin-top:1.5rem;text-align:center;padding:2.2rem;border-radius:24px;background:#182338;color:#fff;
 box-shadow:0 18px 45px rgba(24,35,56,.14)
}
.vision h2{font-family:"Playfair Display",serif;margin:0 0 .6rem}
.vision p{color:#dce2ec;line-height:1.8;max-width:820px;margin:auto}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="topbar">
  <div class="brand">Interview<span>Ace</span></div>
  <div class="eyebrow">Our Story</div>
</div>
<div class="hero">
  <div class="eyebrow">The idea behind the platform</div>
  <h1>The Story Behind InterviewAce</h1>
  <p>Bridging practical interview preparation with modern AI to help candidates prepare with confidence.</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.55, 1], gap="large")
with left:
    st.markdown("""
    <div class="card">
      <div class="eyebrow">Interview preparation, reimagined</div>
      <h2>What is InterviewAce?</h2>
      <p>InterviewAce is an AI-powered platform designed to help job seekers prepare for interviews with confidence. It offers personalized mock interviews, intelligent feedback, and adaptive coaching using powerful AI models.</p>
      <div class="badges">
        <span class="badge">Streamlit</span>
        <span class="badge">Groq · Qwen3 32B</span>
        <span class="badge">Python</span>
        <span class="badge">Computer Vision</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with right:
    try:
        st.image("assets/image.jpeg", use_container_width=True)
    except Exception:
        st.markdown('<div class="card"><h2>InterviewAce</h2><p>AI-powered interview preparation.</p></div>', unsafe_allow_html=True)

st.markdown("""
<div class="vision">
  <div class="eyebrow">Looking ahead</div>
  <h2>Vision for the Future</h2>
  <p>We aim to evolve with AI advancements to deliver hyper-personalized interview simulations, real-time behavioral analysis, and intelligent career growth insights.</p>
</div>
""", unsafe_allow_html=True)

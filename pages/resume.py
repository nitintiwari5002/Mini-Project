import streamlit as st
from core.ai import improve_summary, generate_bullets, resume_score, match_keywords
import tempfile
import html
import pdfkit
from components.navbar import render_navbar
st.set_page_config(page_title="AI Resume Builder", page_icon="📄", layout="wide")
render_navbar("home")

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');


/* =========================================================
   GLOBAL
   ========================================================= */

html,
body,
[class*="css"] {
    font-family: "DM Sans", sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(201,164,92,.14),
            transparent 28%
        ),
        radial-gradient(
            circle at 90% 10%,
            rgba(24,35,56,.08),
            transparent 25%
        ),
        linear-gradient(
            180deg,
            #fbfaf7 0%,
            #f1efe8 100%
        );
}

.block-container {
    max-width: 1200px !important;
    padding-top: 1.2rem !important;
    padding-bottom: 4rem !important;
}


/* =========================================================
   HERO
   ========================================================= */

.hero {
    width: 100%;
    box-sizing: border-box;

    padding: 3.4rem 2.5rem;

    border-radius: 28px;

    background:
        radial-gradient(
            circle at 85% 15%,
            rgba(201,164,92,.20),
            transparent 28%
        ),
        linear-gradient(
            135deg,
            #141f33 0%,
            #263653 100%
        );

    color: #ffffff !important;

    box-shadow:
        0 22px 60px
        rgba(24,35,56,.18);

    margin-bottom: 1.7rem;
}


/* =========================================================
   HERO EYEBROW
   ========================================================= */

.eyebrow {
    text-transform: uppercase;

    letter-spacing: .18em;

    font-size: .72rem;

    font-weight: 800;

    color: #f0d9a4 !important;

    margin-bottom: .55rem;
}


/* =========================================================
   HERO TITLE
   ========================================================= */

.hero h1 {
    font-family:
        "Playfair Display",
        Georgia,
        serif;

    font-size:
        clamp(
            2.4rem,
            5vw,
            3.4rem
        );

    font-weight: 700;

    line-height: 1.1;

    color: #ffffff !important;

    margin:
        .35rem 0
        .7rem;

    letter-spacing: -.02em;

    text-shadow:
        0 2px 8px
        rgba(0,0,0,.22);
}


/* =========================================================
   HERO DESCRIPTION
   ========================================================= */

.hero p {
    max-width: 760px;

    color: #f1f4f8 !important;

    font-size: 1rem;

    font-weight: 500;

    line-height: 1.75;

    margin: 0;

    text-shadow:
        0 1px 3px
        rgba(0,0,0,.20);
}


/* =========================================================
   PANELS
   ========================================================= */

.panel {
    background:
        rgba(
            255,
            255,
            255,
            .97
        );

    border:
        1px solid
        #e2ddd3;

    border-radius: 22px;

    padding: 1.5rem;

    box-shadow:
        0 12px 35px
        rgba(24,35,56,.07);

    margin-bottom: 1rem;
}


/* =========================================================
   PANEL TITLE
   ========================================================= */

.panel-title {
    font-family:
        "Playfair Display",
        Georgia,
        serif;

    font-size: 1.35rem;

    font-weight: 700;

    line-height: 1.3;

    color: #182338 !important;

    margin-bottom: 1rem;
}


/* =========================================================
   STREAMLIT LABELS
   ========================================================= */

.stTextInput label,
.stTextArea label,
.stRadio label,
.stSelectbox label,
.stFileUploader label {

    color: #182338 !important;

    font-size: .88rem !important;

    font-weight: 700 !important;
}


/* =========================================================
   TEXT INPUTS
   ========================================================= */

.stTextInput input,
.stTextArea textarea {

    color: #182338 !important;

    background:
        #ffffff !important;

    border:
        1px solid
        #d5d0c6 !important;

    border-radius:
        12px !important;

    font-family:
        "DM Sans",
        sans-serif !important;

    font-size:
        .92rem !important;

    font-weight:
        500 !important;

    box-shadow:
        none !important;

    transition:
        border-color .2s ease,
        box-shadow .2s ease;
}


/* =========================================================
   PLACEHOLDER
   ========================================================= */

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {

    color:
        #7a8493 !important;

    opacity:
        1 !important;
}


/* =========================================================
   INPUT FOCUS
   ========================================================= */

.stTextInput input:focus,
.stTextArea textarea:focus {

    border-color:
        #c9a45c !important;

    box-shadow:
        0 0 0 2px
        rgba(
            201,
            164,
            92,
            .15
        ) !important;
}


/* =========================================================
   RADIO BUTTON TEXT
   ========================================================= */

.stRadio div[role="radiogroup"] label {

    color:
        #344054 !important;

    font-weight:
        600 !important;
}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button,
.stDownloadButton > button {

    min-height:
        44px !important;

    border-radius:
        12px !important;

    border:
        1px solid
        #c9a45c !important;

    background:
        linear-gradient(
            135deg,
            #c9a45c,
            #dfc485
        ) !important;

    color:
        #182338 !important;

    font-family:
        "DM Sans",
        sans-serif !important;

    font-weight:
        800 !important;

    box-shadow:
        0 8px 22px
        rgba(
            201,
            164,
            92,
            .18
        ) !important;

    transition:
        all .2s ease !important;
}


.stButton > button:hover,
.stDownloadButton > button:hover {

    background:
        linear-gradient(
            135deg,
            #dfc485,
            #ead8ad
        ) !important;

    color:
        #182338 !important;

    transform:
        translateY(-1px);
}


/* =========================================================
   SELECT / INPUT BASE
   ========================================================= */

[data-baseweb="select"] > div {

    background:
        #ffffff !important;

    border:
        1px solid
        #d5d0c6 !important;

    border-radius:
        12px !important;

    color:
        #182338 !important;
}


/* =========================================================
   GENERAL MARKDOWN
   ========================================================= */

.stMarkdown p,
.stMarkdown li {

    color:
        #475467;
}


/* =========================================================
   SUCCESS / ERROR / WARNING
   ========================================================= */

[data-testid="stAlert"] {

    border-radius:
        12px !important;
}


/* =========================================================
   PREVIEW
   ========================================================= */

.preview-wrap {

    border:
        1px solid
        #e2ddd3;

    border-radius:
        20px;

    background:
        #ffffff;

    padding:
        1rem;

    box-shadow:
        0 12px 35px
        rgba(24,35,56,.07);
}


/* =========================================================
   DIVIDERS
   ========================================================= */

hr {

    border-color:
        #e2ddd3 !important;
}


/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 800px) {

    .hero {
        padding:
            2.7rem
            1.5rem;
    }

    .hero h1 {
        font-size:
            2.35rem;
    }

    .panel {
        padding:
            1.2rem;
    }
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
ˀ<div class="hero">
  <div class="eyebrow">ATS + modern design</div>
  <h1>Build a Resume That Gets Noticed.</h1>
  <p>Craft a polished, ATS-friendly resume with AI-assisted writing, structured sections, and a clean professional preview.</p>
</div>
""", unsafe_allow_html=True)

if "generated_html" not in st.session_state:
    st.session_state.generated_html = ""
if "skill_sections" not in st.session_state:
    st.session_state.skill_sections = []

# -----------------------------
# INPUTS
# -----------------------------
st.markdown('<div class="panel"><div class="panel-title">Personal Information</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    name = st.text_input("Full Name", key="name")
    title = st.text_input("Job Title", key="title")
    phone = st.text_input("Phone", key="phone")
with c2:
    email = st.text_input("Email", key="email")
    linkedin = st.text_input("LinkedIn", key="linkedin")
    github = st.text_input("GitHub", key="github")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="panel"><div class="panel-title">Resume Style</div>', unsafe_allow_html=True)
mode = st.radio("Resume Mode", ["ATS (Simple)", "Modern (Styled)"], horizontal=True)
layout = st.radio("Layout (Modern Only)", ["One Column", "Two Column"], horizontal=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="panel"><div class="panel-title">Professional Summary</div>', unsafe_allow_html=True)
summary = st.text_area("Write your summary", key="summary", height=130)
if st.button("Improve Summary"):
    result, err = improve_summary(summary)
    if err:
        st.error(err)
    elif result:
        st.session_state.summary = result
        st.success("Summary improved.")
        st.write(result)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="panel"><div class="panel-title">Experience</div>', unsafe_allow_html=True)
experience = st.text_area("Enter experience (each point on a new line)", key="experience", height=150)
if st.button("Generate Bullet Points"):
    result, err = generate_bullets(title, experience)
    if err:
        st.error(err)
    elif result:
        st.session_state.experience = result
        st.success("Experience improved.")
        st.write(result)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="panel"><div class="panel-title">Projects</div>', unsafe_allow_html=True)
projects = st.text_area("Format: Title | Tech | Bullet1, Bullet2", key="projects", height=130)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="panel"><div class="panel-title">Education</div>', unsafe_allow_html=True)
education = st.text_area("Enter each education detail on a new line", key="education", height=120)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="panel"><div class="panel-title">Technical Skills</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    skill_header = st.text_input("Skill Category", key="skill_header")
with c2:
    skill_values = st.text_input("Skills (comma separated)", key="skill_values")
if st.button("Add Skill Section"):
    if skill_header.strip() and skill_values.strip():
        st.session_state.skill_sections.append((skill_header.strip(), skill_values.strip()))
        st.success(f"Added {skill_header.strip()}")
for header, values in st.session_state.skill_sections:
    st.markdown(f'<span style="display:inline-block;padding:.45rem .7rem;margin:.2rem;border-radius:999px;background:#fbf7ed;border:1px solid #ead8b0;color:#6e5730;"><b>{html.escape(header)}</b>: {html.escape(values)}</span>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="panel"><div class="panel-title">Certifications</div>', unsafe_allow_html=True)
certifications = st.text_input("Comma separated", key="certifications")
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# HELPERS
# -----------------------------
def to_list(text):
    return [line.strip() for line in text.splitlines() if line.strip()]

def format_list(items):
    if not items:
        return ""
    return "<ul>" + "".join(f"<li>{html.escape(item)}</li>" for item in items) + "</ul>"

def format_projects(projects_text):
    output = ""
    for line in projects_text.splitlines():
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split("|")]
        project_title = parts[0] if parts else ""
        tech = parts[1] if len(parts) > 1 else ""
        desc = parts[2] if len(parts) > 2 else ""
        bullets = [x.strip() for x in desc.split(",") if x.strip()]
        if project_title:
            output += f"<p><b>{html.escape(project_title)}</b>"
            if tech:
                output += f" <span style='color:#667085'>| {html.escape(tech)}</span>"
            output += "</p>"
        output += format_list(bullets)
    return output

def format_skills_sections(sections):
    output = ""
    for header, skills in sections:
        items = [x.strip() for x in skills.split(",") if x.strip()]
        if header and items:
            output += f"<p><b>{html.escape(header)}:</b> {html.escape(', '.join(items))}</p>"
    return output

def generate_pdf(resume_html):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdfkit.from_string(resume_html, tmp.name)
        return tmp.name

# -----------------------------
# GENERATE
# -----------------------------
if st.button("Generate Resume", use_container_width=True):
    exp_html = format_list(to_list(experience))
    edu_html = format_list(to_list(education))
    proj_html = format_projects(projects)
    skills_html = format_skills_sections(st.session_state.skill_sections)
    cert_html = format_list([c.strip() for c in certifications.split(",") if c.strip()])

    safe_name = html.escape(name)
    contact_parts = [title, phone, email, linkedin, github]
    contact_line = " | ".join(html.escape(x) for x in contact_parts if x)

    if mode == "ATS (Simple)":
        generated = f"""
<!doctype html>
<html><head><meta charset="utf-8">
<style>
body{{font-family:Arial,sans-serif;color:#222;margin:42px;line-height:1.55}}
h1{{font-size:30px;margin:0 0 5px}}
h2{{font-size:16px;border-bottom:2px solid #222;padding-bottom:5px;margin-top:24px}}
p{{margin:6px 0}} li{{margin:4px 0}}
.contact{{color:#555}}
</style></head><body>
<h1>{safe_name}</h1><p class="contact">{contact_line}</p>
{f"<h2>Professional Summary</h2><p>{html.escape(summary)}</p>" if summary else ""}
{f"<h2>Skills</h2>{skills_html}" if skills_html else ""}
{f"<h2>Experience</h2>{exp_html}" if exp_html else ""}
{f"<h2>Projects</h2>{proj_html}" if proj_html else ""}
{f"<h2>Education</h2>{edu_html}" if edu_html else ""}
{f"<h2>Certifications</h2>{cert_html}" if cert_html else ""}
</body></html>
"""
    elif layout == "One Column":
        generated = f"""
<!doctype html>
<html><head><meta charset="utf-8">
<style>
body{{font-family:Arial,sans-serif;color:#182338;margin:40px;line-height:1.55}}
h1{{font-size:34px;margin:0;text-align:center}} .contact{{text-align:center;color:black}}
.section{{margin-top:22px}} .title{{font-weight:700;letter-spacing:1px;border-bottom:2px solid #c9a45c;padding-bottom:5px;color:black}}
li{{margin:4px 0}}
</style></head><body>
<h1>{safe_name}</h1><p class="contact">{contact_line}</p>
{f"<div class='section'><div class='title'>SUMMARY</div><p>{html.escape(summary)}</p></div>" if summary else ""}
{f"<div class='section'><div class='title'>SKILLS</div>{skills_html}</div>" if skills_html else ""}
{f"<div class='section'><div class='title'>EXPERIENCE</div>{exp_html}</div>" if exp_html else ""}
{f"<div class='section'><div class='title'>PROJECTS</div>{proj_html}</div>" if proj_html else ""}
{f"<div class='section'><div class='title'>EDUCATION</div>{edu_html}</div>" if edu_html else ""}
{f"<div class='section'><div class='title'>CERTIFICATIONS</div>{cert_html}</div>" if cert_html else ""}
</body></html>
"""
    else:
        generated = f"""
<!doctype html>
<html><head><meta charset="utf-8">
<style>
body{{font-family:Arial,sans-serif;color:#182338;margin:34px;line-height:1.5}}
h1{{font-size:34px;margin:0 0 4px}} .contact{{color:#667085;margin-top:0}}
.container{{display:flex;gap:32px;margin-top:25px}} .left{{width:30%;padding-right:22px;border-right:1px solid #ddd}}
.right{{width:70%}} .section{{margin-bottom:22px}}
.title{{font-weight:700;letter-spacing:1px;border-bottom:2px solid #c9a45c;padding-bottom:5px}}
li{{margin:4px 0}}
</style></head><body>
<h1>{safe_name}</h1><p class="contact">{contact_line}</p>
<div class="container">
<div class="left">
{f"<div class='section'><div class='title'>SKILLS</div>{skills_html}</div>" if skills_html else ""}
{f"<div class='section'><div class='title'>CERTIFICATIONS</div>{cert_html}</div>" if cert_html else ""}
{f"<div class='section'><div class='title'>EDUCATION</div>{edu_html}</div>" if edu_html else ""}
</div>
<div class="right">
{f"<div class='section'><div class='title'>SUMMARY</div><p>{html.escape(summary)}</p></div>" if summary else ""}
{f"<div class='section'><div class='title'>EXPERIENCE</div>{exp_html}</div>" if exp_html else ""}
{f"<div class='section'><div class='title'>PROJECTS</div>{proj_html}</div>" if proj_html else ""}
</div>
</div>
</body></html>
"""

    st.session_state.generated_html = generated
    st.success("Resume generated successfully.")

# -----------------------------
# PREVIEW + DOWNLOAD
# -----------------------------
if st.session_state.generated_html:
    st.markdown('<div class="panel"><div class="panel-title">Preview</div>', unsafe_allow_html=True)
    st.components.v1.html(st.session_state.generated_html, height=850, scrolling=True)
    st.download_button("Download HTML", st.session_state.generated_html, "resume.html", "text/html")

    try:
        pdf_file = generate_pdf(st.session_state.generated_html)
        with open(pdf_file, "rb") as f:
            st.download_button("Download PDF", f, "resume.pdf", "application/pdf")
    except Exception:
        st.warning("PDF export requires wkhtmltopdf to be installed and available on your system.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><div class="panel-title">ATS Tools</div>', unsafe_allow_html=True)
    if st.button("Check ATS Score"):
        result, err = resume_score(st.session_state.generated_html)
        if err:
            st.error(err)
        elif result:
            st.markdown(result)

    job_desc = st.text_area("Paste Job Description")
    if st.button("Match Job"):
        result, err = match_keywords(st.session_state.generated_html, job_desc)
        if err:
            st.error(err)
        elif result:
            st.markdown(result)
    st.markdown('</div>', unsafe_allow_html=True)

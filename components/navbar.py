import streamlit as st

# Keep this CSS left-aligned. Indented strings passed to st.markdown()
# are treated as Markdown code blocks and show up on the page.
NAVBAR_CSS = """
<style>
div[data-testid="stToolbar"],
header[data-testid="stHeader"] {
    visibility: hidden;
    height: 0;
}

.st-key-interviewace-navbar {
    background: linear-gradient(135deg, #172238 0%, #243451 100%);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 18px;
    padding: 10px 14px 12px 14px;
    margin-bottom: 28px;
    box-shadow: 0 12px 30px rgba(17, 29, 49, 0.18);
    position: relative;
}

.st-key-interviewace-navbar::before {
    content: "";
    position: absolute;
    top: 0;
    left: 12%;
    right: 12%;
    height: 2px;
    background: linear-gradient(90deg, transparent, #d8b96f, transparent);
    border-radius: 10px;
}

.ia-brand {
    height: 42px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.ia-brand-logo {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    border-radius: 10px;
    background: linear-gradient(135deg, #c9a45c, #ead8ad);
    color: #182338;
    font-family: Arial, sans-serif;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: -0.05em;
    box-shadow: 0 5px 15px rgba(201, 164, 92, 0.22);
}

.ia-brand-text {
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.ia-brand-title {
    color: #ffffff;
    font-family: "DM Sans", Arial, sans-serif;
    font-size: 1.05rem;
    font-weight: 800;
    line-height: 1;
}

.ia-brand-title span {
    color: #e7cf98;
}

.ia-brand-subtitle {
    margin-top: 4px;
    color: rgba(255, 255, 255, 0.50);
    font-family: "DM Sans", Arial, sans-serif;
    font-size: 0.57rem;
    font-weight: 600;
    letter-spacing: 0.10em;
    text-transform: uppercase;
}

.st-key-interviewace-navbar [data-testid="stHorizontalBlock"] {
    align-items: center;
}

.st-key-interviewace-navbar [data-testid="column"] {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 4px !important;
}

.st-key-interviewace-navbar [data-testid="stPageLink-NavLink"] {
    width: 100%;
    min-height: 40px;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 11px;
    border-radius: 10px;
    border: 1px solid transparent;
    background: transparent;
    color: rgba(235, 239, 246, 0.76);
    font-family: "DM Sans", Arial, sans-serif;
    font-size: 0.80rem;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.18s ease;
}

.st-key-interviewace-navbar [data-testid="stPageLink-NavLink"]:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.10);
    color: #ffffff;
    transform: translateY(-1px);
    text-decoration: none;
}

.st-key-interviewace-navbar [data-testid="stPageLink-NavLink"][aria-current="page"] {
    background: linear-gradient(135deg, #c9a45c, #e5ca8c);
    color: #172238;
    border-color: #ead8ad;
    box-shadow: 0 6px 16px rgba(201, 164, 92, 0.22);
    font-weight: 700;
    text-decoration: none;
}

.st-key-interviewace-navbar [data-testid="stPageLink-NavLink"][aria-current="page"]:hover {
    background: linear-gradient(135deg, #dfc485, #f0dfb3);
    color: #172238;
}

.st-key-interviewace-navbar [data-testid="stPageLink-NavLink"][href*="resume"] {
    color: #ead8ad;
    border-color: rgba(234, 216, 173, 0.25);
    background: rgba(234, 216, 173, 0.05);
}

.st-key-interviewace-navbar [data-testid="stPageLink-NavLink"][href*="resume"]:hover {
    background: rgba(234, 216, 173, 0.12);
    border-color: rgba(234, 216, 173, 0.45);
    color: #f3e5bd;
}

.st-key-interviewace-navbar [data-testid="stPageLink-NavLink"][href*="resume"][aria-current="page"] {
    background: linear-gradient(135deg, #c9a45c, #e5ca8c);
    color: #172238;
    border-color: #ead8ad;
}

@media (max-width: 850px) {
    .st-key-interviewace-navbar {
        padding: 9px;
    }
    .ia-brand-subtitle {
        display: none;
    }
    .ia-brand-title {
        font-size: 0.96rem;
    }
    .ia-brand-logo {
        width: 34px;
        height: 34px;
    }
    .st-key-interviewace-navbar [data-testid="stPageLink-NavLink"] {
        padding: 0 7px;
        font-size: 0.72rem;
    }
}

@media (max-width: 650px) {
    .st-key-interviewace-navbar {
        border-radius: 14px;
        padding: 8px;
    }
    .st-key-interviewace-navbar [data-testid="column"] {
        padding: 2px !important;
    }
    .st-key-interviewace-navbar [data-testid="stPageLink-NavLink"] {
        min-height: 36px;
        padding: 0 5px;
        font-size: 0.65rem;
        border-radius: 8px;
    }
}

@media (max-width: 480px) {
    .ia-brand {
        justify-content: center;
        margin-bottom: 7px;
    }
    .st-key-interviewace-navbar [data-testid="stPageLink-NavLink"] {
        font-size: 0.58rem;
        padding: 0 3px;
    }
}
</style>
"""

BRAND_HTML = """
<div class="ia-brand">
  <div class="ia-brand-logo">IA</div>
  <div class="ia-brand-text">
    <div class="ia-brand-title">Interview<span>Ace</span></div>
    <div class="ia-brand-subtitle">AI Career Assistant</div>
  </div>
</div>
"""


def render_navbar(_active_page="home"):
    st.markdown(NAVBAR_CSS, unsafe_allow_html=True)

    with st.container(key="interviewace-navbar"):
        brand_col, home_col, features_col, about_col, resume_col = st.columns(
            [2.45, 0.85, 1.05, 1.00, 1.45],
            gap="small",
        )

        with brand_col:
            st.markdown(BRAND_HTML, unsafe_allow_html=True)

        with home_col:
            st.page_link("pages/home.py", label="⌂  Home", use_container_width=True)

        with features_col:
            st.page_link("pages/features.py", label="✦  Features", use_container_width=True)

        with about_col:
            st.page_link("pages/about_us.py", label="◎  About Us", use_container_width=True)

        with resume_col:
            st.page_link("pages/resume.py", label="▣  Resume Builder", use_container_width=True)

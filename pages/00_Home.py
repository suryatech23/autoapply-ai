import streamlit as st

from autoapply_local import app_page_path, apply_theme, load_applications, load_profile, render_nav

st.set_page_config(page_title="AutoApply AI · Home", page_icon="⚡", layout="wide")
apply_theme(st, hide_sidebar=True)
render_nav(st)

profile = load_profile()
applications = load_applications()
st.markdown('<div class="autoapply-kicker">SBUHacks 2026 · Steel & Steam</div>', unsafe_allow_html=True)
st.markdown("""
<section class="home-hero">
  <div>
    <div class="hero-overline">Your career, engineered around you</div>
    <h1>Make your next<br><span>move unmistakable.</span></h1>
    <p>Find real openings, understand what each role asks for, and build application materials grounded in your actual experience.</p>
    <div class="hero-tags"><span>LIVE ROLE SEARCH</span><span>TRUTHFUL MATCHING</span><span>HUMAN REVIEW</span></div>
  </div>
  <div class="home-hero-visual" aria-hidden="true">
    <div class="hero-orbit">
      <div class="orbit-core">AA</div>
      <div class="orbit-label">A BETTER WAY FORWARD</div>
      <div class="orbit-node n1">REAL ROLE</div>
      <div class="orbit-node n2">YOUR STORY</div>
      <div class="orbit-node n3">NEXT MOVE</div>
    </div>
  </div>
</section>
""", unsafe_allow_html=True)

cta, hint = st.columns([1, 2.4], vertical_alignment="center")
with cta:
    st.page_link(app_page_path("app.py"), label="Open Career Studio", icon="⚡", width="stretch")
with hint:
    st.caption("Start with a resume and a real job description. You stay in control of every edit and application.")

tracked = len(applications)
active = sum(item.get("status") not in {"Closed", "Offer"} for item in applications)
st.markdown('<div class="home-section-title"><span>YOUR SEARCH SNAPSHOT</span><div></div></div>', unsafe_allow_html=True)
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    c1.metric("Career focus", "Role set" if profile.get("target_role") else "Not set")
    c1.caption(profile.get("target_role") or "Choose your target role in Profile")
    c2.metric("Roles in your tracker", tracked)
    c3.metric("Active applications", active)

st.markdown('<div class="home-section-title"><span>FOUR STEPS, ONE CLEAR FLOW</span><div></div></div>', unsafe_allow_html=True)
with st.container(key="home-steps"):
    steps = st.columns(4)
    step_content = [
        (steps[0], "01", "Set your direction", "Save your target role, location, and growth goals."),
        (steps[1], "02", "Find live openings", "Search supported boards and review full job descriptions."),
        (steps[2], "03", "Prepare with evidence", "Compare skills, refine your drafts, and practice interviews."),
        (steps[3], "04", "Apply on your terms", "Open the employer page with materials you have reviewed."),
    ]
    for column, number, heading, body in step_content:
        with column:
            st.markdown(f'<div class="step-card"><span class="step-number">{number}</span><h3>{heading}</h3><p>{body}</p></div>', unsafe_allow_html=True)

st.markdown('<div class="home-section-title"><span>PICK UP WHERE YOU LEFT OFF</span><div></div></div>', unsafe_allow_html=True)
with st.container(key="home-quicklinks"):
    left, right = st.columns(2)
    with left, st.container(border=True):
        st.markdown("### 👤 Career Profile")
        st.caption("Update target roles, location preferences, and skills you want to build.")
        st.page_link(app_page_path("pages/02_Profile.py"), label="Edit career profile", icon="👤", width="stretch")
    with right, st.container(border=True):
        st.markdown("### 🗂️ Application Tracker")
        st.caption("Keep next steps, follow-up dates, and notes in a private local file on this device.")
        st.page_link(app_page_path("pages/01_Application_Tracker.py"), label="View your tracker", icon="🗂️", width="stretch")

st.info("Privacy: profile preferences and saved roles stay in local files. Resume uploads stay in this session. AI features send selected content only after you approve the in-app notice.")

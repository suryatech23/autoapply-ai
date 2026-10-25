import streamlit as st

from autoapply_local import apply_theme, load_profile, render_nav, save_profile

st.set_page_config(page_title="AutoApply AI · Profile", page_icon="👤", layout="wide")
apply_theme(st, hide_sidebar=True)
render_nav(st)
st.markdown('<div class="autoapply-kicker">Your preferences and growth plan</div>', unsafe_allow_html=True)
st.title("Career profile")
st.caption("Use these preferences to speed up job searches and keep your growth goals visible. Your uploaded resume is not stored in this profile.")

profile = load_profile()
countries = ["USA", "India", "United Kingdom", "Canada", "Germany", "Australia", "United Arab Emirates", "Singapore", "Custom / Type Any Country"]
work_modes = ["Any", "Remote", "Hybrid", "On-site"]
job_types = ["Any", "Internship", "Full-time", "Part-time", "Contract"]
seniority_levels = ["Any", "Student", "Entry level", "Mid-level", "Senior"]

with st.form("career_profile_form"):
    target_role = st.text_input("Target role or search phrase", value=profile.get("target_role", ""), placeholder="Software Engineer Intern")
    country_value = profile.get("target_country", "USA")
    country_index = countries.index(country_value) if country_value in countries else countries.index("Custom / Type Any Country")
    target_country = st.selectbox("Preferred country", countries, index=country_index)
    if target_country == "Custom / Type Any Country":
        target_country = st.text_input("Country name", value=profile.get("target_country", ""), placeholder="Japan")
    preferred_location = st.text_input("City, state, or remote preference", value=profile.get("preferred_location", ""), placeholder="New York, NY · remote")
    c1, c2, c3 = st.columns(3)
    with c1:
        work_mode = st.selectbox("Work style", work_modes, index=work_modes.index(profile.get("work_mode", "Any")) if profile.get("work_mode") in work_modes else 0)
    with c2:
        job_type = st.selectbox("Role type", job_types, index=job_types.index(profile.get("job_type", "Any")) if profile.get("job_type") in job_types else 0)
    with c3:
        seniority = st.selectbox("Career stage", seniority_levels, index=seniority_levels.index(profile.get("seniority", "Any")) if profile.get("seniority") in seniority_levels else 0)
    industries = st.text_input("Industries of interest", value=", ".join(profile.get("industries", [])), placeholder="Climate tech, healthcare, education")
    board_options = ["indeed", "zip_recruiter", "glassdoor", "google"]
    preferred_boards = st.multiselect("Preferred job boards", board_options, default=[site for site in profile.get("preferred_boards", ["indeed", "google"]) if site in board_options], format_func=lambda site: {"indeed": "Indeed", "zip_recruiter": "ZipRecruiter", "glassdoor": "Glassdoor", "google": "Google Jobs"}[site])
    skills = st.text_area("Skills you want to build", value="\n".join(profile.get("skills_to_build", [])), placeholder="Add one skill per line")
    save = st.form_submit_button("Save career preferences", type="primary", width="stretch")

if save:
    country = target_country.strip()
    saved = {
        "target_role": target_role,
        "target_country": country,
        "preferred_location": preferred_location,
        "work_mode": work_mode,
        "job_type": job_type,
        "seniority": seniority,
        "industries": [item.strip() for item in industries.split(",") if item.strip()],
        "preferred_boards": preferred_boards,
        "skills_to_build": [item.strip() for item in skills.splitlines() if item.strip()],
    }
    save_profile(saved)
    st.success("Career preferences saved privately on this device.")

analysis = st.session_state.get("analysis_result") or {}
gaps = [str(item).strip() for item in analysis.get("missing_skills", []) if str(item).strip()]
if gaps:
    st.divider()
    st.subheader("Turn role gaps into a growth plan")
    st.caption("These are terms not found verbatim in the current resume. Add them to your plan only if they reflect skills you want to learn or clarify.")
    st.write(" · ".join(gaps))
    if st.button("Add these skills to my growth plan", type="primary"):
        profile = load_profile()
        plan = list(profile.get("skills_to_build", []))
        for gap in gaps:
            if gap not in plan:
                plan.append(gap)
        profile["skills_to_build"] = plan
        save_profile(profile)
        st.success("Growth plan updated. These are goals, not claims about your current experience.")

if profile.get("skills_to_build"):
    st.divider()
    st.subheader("Current growth plan")
    for skill in profile["skills_to_build"]:
        st.markdown(f"- {skill}")
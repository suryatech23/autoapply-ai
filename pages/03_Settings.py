import os

import streamlit as st

from autoapply_local import app_page_path, apply_theme, load_applications, load_profile, public_demo_mode, remove_saved_provider_key, render_nav, save_applications, save_profile

st.set_page_config(page_title="AutoApply AI · Settings", page_icon="⚙️", layout="wide")
apply_theme(st, hide_sidebar=True)
render_nav(st)
PUBLIC_DEMO = public_demo_mode()
st.markdown(
    '<div class="autoapply-kicker">Public demo · privacy and preferences</div>'
    if PUBLIC_DEMO
    else '<div class="autoapply-kicker">Privacy, providers, and local data</div>',
    unsafe_allow_html=True,
)
st.title("Settings")
st.caption(
    "This hosted demo keeps profile and tracker data in your current browser session."
    if PUBLIC_DEMO
    else "Review where your data lives and manage this device's saved career-search data."
)


def provider_key_available(name):
    try:
        configured = str(st.secrets.get(name, "") or "").strip()
    except Exception:
        configured = ""
    return bool(configured or os.environ.get(name, "").strip())


groq_ready = provider_key_available("GROQ_API_KEY")
gemini_ready = provider_key_available("GEMINI_API_KEY")
auth_ready = False
try:
    auth = st.secrets.get("auth", {})
    auth_ready = all(str(auth.get(key, "") or "").strip() for key in ("client_id", "client_secret", "cookie_secret", "redirect_uri", "server_metadata_url"))
except Exception:
    pass

c1, c2, c3 = st.columns(3)
c1.metric("Google sign-in", "Configured" if auth_ready else "Guest demo")
if PUBLIC_DEMO:
    c2.metric("Profile and tracker", "Session only")
    c3.metric("Provider key storage", "Never saved")
else:
    c2.metric("Groq key", "Saved" if groq_ready else "Not saved")
    c3.metric("Gemini key", "Saved" if gemini_ready else "Not saved")

st.markdown("### AI provider keys")
if PUBLIC_DEMO:
    st.write("Enter a provider key in Career Studio only if you want to use AI features. The hosted demo keeps that key in your browser session and never writes it to shared app files.")
    st.page_link(app_page_path("app.py"), label="Open provider setup in Career Studio", icon="⚡")
    st.caption("The key is sent to the selected provider only when you run an AI feature. This demo does not include a shared provider key.")
else:
    st.write("Keys are stored only in this app's local ignored settings file when you choose Save key on this device in the Career Studio sidebar. They are sent to the selected provider only when you run an AI feature.")
    st.page_link(app_page_path("app.py"), label="Open provider setup in Career Studio", icon="⚡")
    st.caption("Removing a key here removes the local copy. It does not revoke the key at Groq or Google; use the provider's account page if you need to revoke it there.")

    with st.form("remove_provider_key_form"):
        provider = st.selectbox("Stored key to remove", ["Gemini", "Groq"])
        setting = "GEMINI_API_KEY" if provider == "Gemini" else "GROQ_API_KEY"
        confirm = st.checkbox("I understand this only removes the saved copy on this device.")
        remove = st.form_submit_button("Remove saved key from this device", disabled=not confirm)
    if remove:
        try:
            remove_saved_provider_key(setting)
            st.session_state[f"disabled_api_key_{setting}"] = True
            st.session_state.pop(f"saved_api_key_{setting}", None)
            st.success(f"{provider} key removed from the local settings file.")
        except Exception:
            st.error("The key could not be removed from local settings.")

st.divider()
st.markdown("### Session data" if PUBLIC_DEMO else "### Local career data")
st.write(
    "The hosted demo keeps saved roles and career preferences only in this browser session. They are not written to shared files and may be cleared when the session ends."
    if PUBLIC_DEMO
    else "The application tracker and career preferences are stored in the local .streamlit folder and are excluded from source control. Resume PDFs and generated drafts remain in the active browser session."
)
confirm_label = (
    "I want to clear saved roles and profile preferences from this session."
    if PUBLIC_DEMO
    else "I want to clear saved roles and profile preferences from this device."
)
confirm_clear = st.checkbox(confirm_label)
left, right = st.columns(2)
with left:
    if st.button("Clear tracker for this session" if PUBLIC_DEMO else "Clear application tracker", disabled=not confirm_clear):
        save_applications([])
        st.success("Session tracker cleared." if PUBLIC_DEMO else "Saved roles cleared.")
with right:
    if st.button("Clear profile for this session" if PUBLIC_DEMO else "Clear career profile", disabled=not confirm_clear):
        save_profile({})
        st.success("Session profile cleared." if PUBLIC_DEMO else "Career preferences cleared.")

st.divider()
st.markdown("### Application safety")
st.info("AutoApply prepares drafts and opens the employer's original page. It does not submit applications or send your personal details to employers. Review every answer and submit on the employer's site yourself.")
st.markdown("### Microphone privacy")
st.caption("The coach microphone is opt-in. Audio is sent for transcription only after you check the separate audio consent and press Transcribe. The app does not save recordings to disk.")
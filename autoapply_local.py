import json
import os
import re

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
PRIVATE_DIR = os.path.join(APP_ROOT, ".streamlit")
APPLICATIONS_PATH = os.path.join(PRIVATE_DIR, "application_tracker.json")
PROFILE_PATH = os.path.join(PRIVATE_DIR, "career_profile.json")
_ALLOWED_SECRET_NAMES = {"GROQ_API_KEY", "GEMINI_API_KEY"}


def app_page_path(relative_path):
    """Resolve a multipage target against the installed app directory."""
    return os.path.abspath(os.path.join(APP_ROOT, relative_path))


def _load_json(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as data_file:
            value = json.load(data_file)
        return value
    except (OSError, ValueError, TypeError):
        return fallback


def _save_json(path, value):
    """Write local state with a temporary file so an interrupted save stays recoverable."""
    os.makedirs(PRIVATE_DIR, exist_ok=True)
    temporary_path = path + ".tmp"
    try:
        with open(temporary_path, "w", encoding="utf-8", newline="\n") as data_file:
            json.dump(value, data_file, ensure_ascii=False, indent=2)
            data_file.write("\n")
        os.replace(temporary_path, path)
    finally:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)


def load_applications():
    items = _load_json(APPLICATIONS_PATH, [])
    return items if isinstance(items, list) else []


def save_applications(items):
    if not isinstance(items, list):
        raise ValueError("Application tracker data must be a list.")
    _save_json(APPLICATIONS_PATH, items[:500])


def load_profile():
    value = _load_json(PROFILE_PATH, {})
    return value if isinstance(value, dict) else {}


def save_profile(profile):
    if not isinstance(profile, dict):
        raise ValueError("Career profile data must be an object.")
    allowed = {
        "target_role", "target_country", "preferred_location", "work_mode",
        "job_type", "seniority", "industries", "skills_to_build", "preferred_boards",
    }
    cleaned = {key: profile[key] for key in allowed if key in profile}
    for key, value in list(cleaned.items()):
        if key in {"industries", "skills_to_build", "preferred_boards"}:
            if not isinstance(value, list):
                value = []
            cleaned[key] = list(dict.fromkeys(str(item).strip()[:100] for item in value if str(item).strip()))[:40]
        else:
            cleaned[key] = str(value or "").strip()[:500]
    _save_json(PROFILE_PATH, cleaned)


def remove_saved_provider_key(setting):
    """Clear only a supported local provider key; OAuth settings are left intact."""
    if setting not in _ALLOWED_SECRET_NAMES:
        raise ValueError("Unsupported AI provider setting.")
    secrets_path = os.path.join(PRIVATE_DIR, "secrets.toml")
    if not os.path.isfile(secrets_path):
        return
    with open(secrets_path, "r", encoding="utf-8") as secrets_file:
        existing = secrets_file.read()
    parts = re.split(r"(?m)(?=^\[)", existing, maxsplit=1)
    root_settings = parts[0] if parts else ""
    sections = parts[1] if len(parts) > 1 else ""
    pattern = re.compile(rf"(?m)^{re.escape(setting)}[ \t]*=.*$")
    replacement = f"{setting} = \"\""
    if pattern.search(root_settings):
        root_settings = pattern.sub(lambda _match: replacement, root_settings, count=1)
    else:
        root_settings = root_settings.rstrip() + ("\n" if root_settings.strip() else "") + replacement + "\n"
    _save_text(secrets_path, root_settings + sections)


def _save_text(path, text):
    os.makedirs(PRIVATE_DIR, exist_ok=True)
    temporary_path = path + ".tmp"
    try:
        with open(temporary_path, "w", encoding="utf-8", newline="\n") as data_file:
            data_file.write(text)
        os.replace(temporary_path, path)
    finally:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)


def apply_theme(st, hide_sidebar=False):
    sidebar_rule = (
        '[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] '
        '{ display: none !important; }'
        if hide_sidebar
        else '[data-testid="stSidebar"] { background: rgba(8, 18, 31, .96); '
             'border-right: 1px solid rgba(148, 163, 184, .14); }'
    )
    css = """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
      :root {
        --aa-ink: #07101b; --aa-panel: rgba(13, 24, 40, .82);
        --aa-line: rgba(166, 190, 216, .16); --aa-text: #f4f7fb;
        --aa-muted: #9aaabd; --aa-mint: #71f0d4; --aa-copper: #ff9867;
        --aa-lilac: #b89bff;
      }
      html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
      h1, h2, h3, h4, [data-testid="stMetricValue"] { font-family: 'Space Grotesk', 'DM Sans', sans-serif !important; letter-spacing: -.035em; }
      .stApp {
        background-color: var(--aa-ink);
        background-image:
          linear-gradient(rgba(146, 176, 208, .025) 1px, transparent 1px),
          linear-gradient(90deg, rgba(146, 176, 208, .025) 1px, transparent 1px),
          radial-gradient(920px circle at 84% 0%, rgba(130, 91, 255, .17), transparent 51%),
          radial-gradient(760px circle at 5% 14%, rgba(42, 226, 194, .11), transparent 57%),
          linear-gradient(155deg, #091625 0%, #050a12 62%, #0b1020 100%);
        background-size: 48px 48px, 48px 48px, auto, auto, auto;
        background-attachment: fixed; color: var(--aa-text);
      }
      [data-testid="stHeader"] { background: rgba(5, 10, 18, .42); }
      .block-container { max-width: 1480px; padding-top: .6rem; padding-bottom: 4rem; }
      [data-testid="stSidebarNav"] { display: none !important; }
      [data-testid="stSidebar"] { background: rgba(7, 15, 27, .96); border-right: 1px solid var(--aa-line); }
      [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(22, 37, 57, .9), rgba(9, 19, 33, .9));
        border: 1px solid var(--aa-line); padding: 1.1rem 1.2rem; border-radius: 18px;
        box-shadow: inset 0 1px rgba(255,255,255,.035), 0 14px 38px rgba(0,0,0,.16);
      }
      [data-testid="stMetricLabel"] { color: var(--aa-muted); font-weight: 600; }
      [data-testid="stMetricValue"] { color: var(--aa-text); }
      [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(150deg, rgba(17, 31, 49, .85), rgba(9, 18, 31, .72));
        border-color: var(--aa-line); border-radius: 20px;
        box-shadow: inset 0 1px rgba(255,255,255,.035), 0 18px 44px rgba(0,0,0,.12);
      }
      .stButton button, .stDownloadButton button, .stLinkButton a {
        min-height: 44px; white-space: normal; line-height: 1.25;
        border-radius: 13px; font-weight: 700; border: 1px solid rgba(136, 171, 201, .22);
        transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
      }
      .stButton button[kind="primary"] {
        color: #07141a; border: 0;
        background: linear-gradient(105deg, #75f3d5 0%, #7dd8f4 50%, #c5a3ff 100%);
        box-shadow: 0 8px 25px rgba(81, 224, 202, .18);
      }
      .stButton button:hover, .stDownloadButton button:hover, .stLinkButton a:hover {
        transform: translateY(-2px); border-color: rgba(113, 240, 212, .7);
        box-shadow: 0 12px 28px rgba(34, 211, 238, .14);
      }
      .stButton button:focus-visible, .stDownloadButton button:focus-visible, .stLinkButton a:focus-visible,
      [data-testid="stPageLink"] a:focus-visible { outline: 3px solid var(--aa-mint); outline-offset: 3px; }
      [data-baseweb="input"] > div, [data-baseweb="select"] > div,
      [data-baseweb="textarea"] > div, [data-testid="stTextArea"] textarea {
        background: rgba(5, 13, 23, .7); border-color: rgba(166, 190, 216, .2); border-radius: 12px;
      }
      [data-testid="stFileUploader"] section {
        border: 1px dashed rgba(113, 240, 212, .48); border-radius: 18px;
        background: linear-gradient(130deg, rgba(113,240,212,.055), rgba(184,155,255,.07));
      }
      [data-testid="stExpander"] { border: 1px solid var(--aa-line); border-radius: 17px; background: rgba(10, 20, 34, .68); }
      .stTabs [data-baseweb="tab-list"] { gap: .45rem; border-bottom: 1px solid var(--aa-line); overflow-x:auto; flex-wrap:nowrap; }
      .stTabs [data-baseweb="tab"] { border-radius: 12px 12px 0 0; padding: .7rem .95rem; white-space:nowrap; flex:0 0 auto; }
      [data-testid="stAlert"] { border-radius: 15px; }
      [data-testid="stDataFrame"], [data-testid="stTable"] { max-width:100%; overflow-x:auto; }
      [data-testid="stText"], pre, code { overflow-wrap:anywhere; }
      .stTabs [aria-selected="true"] { color: var(--aa-mint); }
      .stProgress > div > div > div { background: linear-gradient(90deg, var(--aa-mint), #8ed9ff, var(--aa-lilac)); }
      .autoapply-kicker { color: var(--aa-mint); letter-spacing: .16em; text-transform: uppercase; font-size: .72rem; font-weight: 800; }
      .autoapply-hero { padding: 1.4rem 0 .6rem; }
      div.st-key-autoapply-nav {
        position: relative; z-index: 2; margin-bottom: 1.6rem; padding: .45rem .65rem;
        border: 1px solid rgba(166,190,216,.17); border-radius: 19px;
        background: linear-gradient(100deg, rgba(8,17,29,.94), rgba(15,23,40,.83));
        box-shadow: 0 14px 38px rgba(0,0,0,.22), inset 0 1px rgba(255,255,255,.04);
        backdrop-filter: blur(18px);
      }
      .aa-brand { display: flex; align-items: center; gap: .7rem; min-height: 2.8rem; white-space: nowrap; }
      .aa-mark { display:grid; place-items:center; width:2.25rem; height:2.25rem; border-radius:.75rem; color:#07141a; font:800 .75rem 'Space Grotesk',sans-serif; background:linear-gradient(140deg,var(--aa-mint),#83dafa 55%,var(--aa-lilac)); box-shadow:0 0 26px rgba(113,240,212,.18); }
      .aa-brand-copy { display:flex; flex-direction:column; line-height:1.05; }
      .aa-brand-copy b { color:#f6fbff; font:700 .82rem 'Space Grotesk',sans-serif; letter-spacing:.08em; }
      .aa-brand-copy small { color:var(--aa-muted); font-size:.56rem; letter-spacing:.12em; margin-top:.28rem; }
      div.st-key-autoapply-nav [data-testid="stPageLink"] a { min-height:2.65rem; font-weight:700; border-radius:12px; text-align:center; }
      div.st-key-autoapply-nav [data-testid="stPageLink"] a:hover { background:rgba(113,240,212,.09); color:var(--aa-mint); }
      div.st-key-autoapply-nav .stButton button { min-height:2.65rem; background:rgba(255,152,103,.08); border-color:rgba(255,152,103,.22); color:#ffc1a0; }
      .home-hero {
        position:relative; overflow:hidden; display:grid; grid-template-columns:1.5fr .8fr; gap:2rem;
        align-items:center; margin:.8rem 0 1.5rem; padding:clamp(1.5rem,4vw,3.4rem);
        border:1px solid rgba(151,178,204,.2); border-radius:30px;
        background:radial-gradient(ellipse at 82% 18%,rgba(184,155,255,.18),transparent 38%),
          radial-gradient(ellipse at 15% 100%,rgba(113,240,212,.1),transparent 42%),
          linear-gradient(125deg,rgba(17,32,51,.96),rgba(7,14,25,.96));
        box-shadow:0 32px 90px rgba(0,0,0,.32), inset 0 1px rgba(255,255,255,.06);
      }
      .home-hero:after { content:""; position:absolute; width:310px; height:310px; right:18%; top:-260px; border:1px solid rgba(113,240,212,.14); border-radius:50%; box-shadow:0 0 0 32px rgba(113,240,212,.025),0 0 0 65px rgba(184,155,255,.025); pointer-events:none; }
      .hero-overline,.studio-overline { color:var(--aa-mint); font:700 .7rem 'DM Sans',sans-serif; letter-spacing:.19em; text-transform:uppercase; }
      .home-hero h1,.studio-hero h1 { color:#f6f8fc; font:700 clamp(2.6rem,5.5vw,5.3rem)/.99 'Space Grotesk',sans-serif; letter-spacing:-.065em; margin:.9rem 0 1.1rem; }
      .home-hero h1 span,.studio-hero h1 span { background:linear-gradient(95deg,#76f0d5 0%,#91dfff 48%,#c0a0ff 100%); -webkit-background-clip:text; background-clip:text; color:transparent; }
      .home-hero p,.studio-hero p { color:#b4c0ce; font-size:clamp(1rem,1.5vw,1.15rem); line-height:1.7; max-width:690px; margin:0; }
      .hero-tags { display:flex; flex-wrap:wrap; gap:.5rem; margin-top:1.5rem; }
      .hero-tags span { padding:.42rem .68rem; border:1px solid rgba(166,190,216,.18); border-radius:999px; color:#ced9e4; background:rgba(4,11,20,.42); font-size:.68rem; font-weight:700; letter-spacing:.06em; }
      .home-hero-visual { position:relative; min-height:310px; display:grid; place-items:center; }
      .hero-orbit { position:relative; width:min(285px,78vw); aspect-ratio:1; border:1px solid rgba(113,240,212,.32); border-radius:50%; display:grid; place-items:center; background:radial-gradient(circle,rgba(113,240,212,.11),rgba(184,155,255,.08) 43%,transparent 70%); box-shadow:0 0 65px rgba(113,240,212,.09),inset 0 0 55px rgba(184,155,255,.08); }
      .hero-orbit:before,.hero-orbit:after { content:""; position:absolute; inset:12%; border:1px solid rgba(184,155,255,.34); border-radius:50%; transform:rotateX(65deg) rotate(-24deg); }
      .hero-orbit:after { inset:20%; border-color:rgba(255,152,103,.4); transform:rotateX(65deg) rotate(33deg); }
      .orbit-core { z-index:1; width:92px; height:92px; border-radius:28px; display:grid; place-items:center; color:#06141a; font:800 1.45rem 'Space Grotesk',sans-serif; background:linear-gradient(145deg,#76f0d5,#8bd5f5 55%,#c0a0ff); box-shadow:0 0 48px rgba(113,240,212,.3); transform:rotate(-7deg); }
      .orbit-label { position:absolute; top:12%; right:-5%; padding:.55rem .75rem; border:1px solid rgba(166,190,216,.2); border-radius:12px; color:#e9f1f8; background:rgba(7,15,27,.88); font-size:.63rem; letter-spacing:.11em; }
      .orbit-node { position:absolute; padding:.48rem .68rem; border:1px solid rgba(166,190,216,.2); border-radius:11px; color:#cbd7e4; background:rgba(7,15,27,.88); font-size:.68rem; }
      .orbit-node.n1 { left:-9%; top:28%; } .orbit-node.n2 { right:-12%; bottom:28%; } .orbit-node.n3 { left:8%; bottom:4%; }
      .home-stats { margin:1.3rem 0 2.1rem; }
      .landing-hero {
        border-color:rgba(151,178,204,.2); border-radius:28px;
        background:radial-gradient(ellipse at 86% 0%,rgba(184,155,255,.16),transparent 42%),
          linear-gradient(135deg,rgba(16,31,50,.96),rgba(7,14,25,.94));
        box-shadow:0 30px 82px rgba(0,0,0,.32),inset 0 1px rgba(255,255,255,.05);
      }
      .landing-badge { color:var(--aa-mint); border-color:rgba(113,240,212,.32); background:rgba(113,240,212,.08); letter-spacing:.08em; }
      .landing-title { font-family:'Space Grotesk',sans-serif; background:linear-gradient(110deg,#fff 0%,#b9cad9 45%,#79efd5 100%); -webkit-background-clip:text; }
      .landing-desc { color:#afbdcc; }
      .auth-box { border-color:var(--aa-line); background:rgba(11,22,37,.78); box-shadow:0 26px 72px rgba(0,0,0,.28),inset 0 1px rgba(255,255,255,.04); }
      .card-stat { border-color:var(--aa-line); background:linear-gradient(145deg,rgba(22,37,57,.88),rgba(9,18,31,.9)); }
      .card-stat-num { color:var(--aa-mint); font-family:'Space Grotesk',sans-serif; }
      .home-section-title { display:flex; align-items:center; gap:.7rem; margin:2rem 0 1rem; }
      .home-section-title span { color:var(--aa-mint); font:700 .68rem 'DM Sans',sans-serif; letter-spacing:.14em; }
      .step-card { min-height:180px; padding:1.15rem; border:1px solid rgba(166,190,216,.16); border-radius:18px; background:linear-gradient(145deg,rgba(16,29,46,.86),rgba(8,16,28,.78)); }
      .step-number { display:inline-grid; place-items:center; width:2.2rem; height:2.2rem; border-radius:11px; color:#06141a; background:linear-gradient(145deg,var(--aa-mint),#91dfff); font:800 .75rem 'Space Grotesk',sans-serif; }
      .step-card h3 { margin:.9rem 0 .55rem; color:#f3f7fb; font:650 1.02rem 'Space Grotesk',sans-serif; letter-spacing:-.025em; }
      .step-card p { color:var(--aa-muted); font-size:.86rem; line-height:1.6; margin:0; }
      .studio-hero {
        position:relative; overflow:hidden; display:grid; grid-template-columns:1.55fr .8fr; gap:1.8rem; align-items:center;
        margin:.5rem 0 1.7rem; padding:clamp(1.3rem,3vw,2.4rem); border:1px solid rgba(151,178,204,.18); border-radius:26px;
        background:radial-gradient(ellipse at 84% 0%,rgba(184,155,255,.15),transparent 43%),linear-gradient(120deg,rgba(15,29,47,.96),rgba(7,14,25,.92));
        box-shadow:0 25px 72px rgba(0,0,0,.26),inset 0 1px rgba(255,255,255,.05);
      }
      .studio-hero h1 { font-size:clamp(2.25rem,4.4vw,4.2rem); margin:.7rem 0 .85rem; }
      .studio-hero p { font-size:1rem; max-width:700px; }
      .studio-visual { position:relative; padding:1.1rem; border:1px solid rgba(166,190,216,.17); border-radius:20px; background:rgba(4,11,20,.54); box-shadow:inset 0 1px rgba(255,255,255,.04); }
      .studio-visual-head { display:flex; justify-content:space-between; align-items:center; color:#b8c5d3; font-size:.62rem; font-weight:800; letter-spacing:.12em; }
      .studio-live { color:var(--aa-mint); }
      .studio-step { display:flex; align-items:center; gap:.8rem; padding:.8rem 0; border-bottom:1px solid rgba(166,190,216,.1); }
      .studio-step:last-child { border-bottom:0; }
      .studio-step-number { display:grid; place-items:center; flex:0 0 2rem; width:2rem;height:2rem;border:1px solid rgba(113,240,212,.3);border-radius:10px;color:var(--aa-mint);font:700 .7rem 'Space Grotesk',sans-serif; }
      .studio-step b { display:block; color:#e9eff6; font-size:.82rem; }
      .studio-step small { color:var(--aa-muted); font-size:.69rem; }
      @media (max-width: 900px) {
        .home-hero,.studio-hero { grid-template-columns:1fr; }
        .home-hero-visual { min-height:280px; }
      }
      @media (max-width: 760px) {
        [data-testid="stAppViewContainer"] main .block-container { padding-left:1rem !important; padding-right:1rem !important; }
        [data-testid="stHorizontalBlock"] { display:grid !important; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.75rem; }
        [data-testid="stHorizontalBlock"] > [data-testid="column"] { width:100% !important; min-width:0 !important; flex:1 1 auto !important; }
        [data-testid="stMetric"] { min-width:0; padding:.9rem; }
        .stMarkdown h1 { font-size:clamp(2rem,7vw,3.1rem); }
        .stMarkdown h2 { font-size:clamp(1.45rem,5vw,2rem); }
        [data-testid="stFileUploader"] section { padding:.8rem; }
        div.st-key-home-steps [data-testid="stHorizontalBlock"] { display:grid !important; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.7rem; }
        div.st-key-home-steps [data-testid="column"] { width:100% !important; min-width:0 !important; flex:1 1 45% !important; }
        div.st-key-home-quicklinks [data-testid="stHorizontalBlock"] { display:grid !important; grid-template-columns:1fr; gap:.7rem; }
        div.st-key-home-quicklinks [data-testid="column"] { width:100% !important; min-width:0 !important; flex:1 1 100% !important; }
        div.st-key-autoapply-nav [data-testid="stHorizontalBlock"] { display:grid !important; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.4rem; }
        div.st-key-autoapply-nav [data-testid="column"] { width:100% !important; min-width:0 !important; flex:1 1 30% !important; }
        div.st-key-autoapply-nav [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child { grid-column:1/-1; }
        div.st-key-autoapply-nav [data-testid="stPageLink"] a { min-height:2.65rem; white-space:nowrap; font-size:.72rem; }
        .step-card { min-height:150px; }
      }
      @media (max-width: 480px) {
        [data-testid="stAppViewContainer"] main .block-container { padding-left:.7rem !important; padding-right:.7rem !important; }
        [data-testid="stHorizontalBlock"] { grid-template-columns:1fr; }
        [data-testid="stHorizontalBlock"] > [data-testid="column"] { grid-column:1/-1 !important; }
        div.st-key-home-steps [data-testid="stHorizontalBlock"] { grid-template-columns:repeat(2,minmax(0,1fr)); }
        div.st-key-home-steps [data-testid="stHorizontalBlock"] > [data-testid="column"] { grid-column:auto !important; }
        div.st-key-autoapply-nav [data-testid="stHorizontalBlock"] { grid-template-columns:repeat(3,minmax(0,1fr)) !important; }
        div.st-key-autoapply-nav [data-testid="stHorizontalBlock"] > [data-testid="column"] { grid-column:auto !important; }
        div.st-key-autoapply-nav [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child { grid-column:1/-1 !important; }
        .home-hero,.studio-hero { padding:1.25rem; border-radius:21px; }
        .home-hero h1,.studio-hero h1 { font-size:clamp(2.25rem,10vw,3.3rem); }
        .home-hero-visual { min-height:250px; }
        .hero-orbit { width:min(230px,68vw); }
        .orbit-node.n1 { left:-4%; }
        .orbit-node.n2 { right:-5%; }
        .step-card { min-height:165px; padding:.85rem; }
        .aa-brand-copy small { font-size:.52rem; }
      }
      @media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition:none !important; animation:none !important; scroll-behavior:auto !important; } }
      __SIDEBAR_RULE__
    </style>
    """.replace("__SIDEBAR_RULE__", sidebar_rule)
    st.markdown(css, unsafe_allow_html=True)


def _handle_logout(st):
    try:
        if bool(st.user.is_logged_in):
            st.logout()
            return
    except Exception:
        pass

    st.session_state["authenticated"] = False
    st.session_state["user_info"] = {
        "name": "Guest session",
        "email": "Local session · no account connected",
    }
    clear_keys = {
        "analysis_result", "latex_resume", "active_job_hash",
        "active_job_description", "scraped_jobs",
    }
    for key in list(st.session_state.keys()):
        if key in clear_keys or key.startswith(("coach_messages_", "coach_audio_", "coach_transcript_", "resume_edit_")):
            st.session_state.pop(key, None)
    st.switch_page(app_page_path("app.py"))


def render_nav(st):
    pages = [
        ("pages/00_Home.py", "Home", "🏠"),
        ("app.py", "Studio", "⚡"),
        ("pages/01_Application_Tracker.py", "Applications", "🗂️"),
        ("pages/02_Profile.py", "Profile", "👤"),
        ("pages/03_Settings.py", "Settings", "⚙️"),
    ]
    with st.container(key="autoapply-nav"):
        columns = st.columns([1.65, .85, .85, 1.25, .9, .9, 1.0], vertical_alignment="center")
        with columns[0]:
            st.markdown(
                '<div class="aa-brand"><span class="aa-mark">AA</span>'
                '<span class="aa-brand-copy"><b>AUTOAPPLY</b><small>CAREER WORKSPACE</small></span></div>',
                unsafe_allow_html=True,
            )
        for column, (path, label, icon) in zip(columns[1:], pages):
            with column:
                st.page_link(app_page_path(path), label=label, icon=icon, width="stretch")
        with columns[-1]:
            if st.button("Log out", key="global_logout_button", width="stretch", help="End this AutoApply session"):
                _handle_logout(st)

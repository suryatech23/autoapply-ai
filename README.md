# AutoApply AI

**A career workspace for turning a real job description and your real experience into an application packet you can review.**

AutoApply helps students organize a job search, understand what a role asks for, and prepare truthful, role-specific materials. It combines live job search, a transparent keyword coverage check, resume and cover-letter drafts, interview practice, and a local application tracker in one Streamlit app.

> Built for student job seekers and prepared for the SBUHacks 2026 demo. Check the event rules and describe the project timeline and AI assistance accurately in any submission.

## What it does

- **Search roles:** query supported boards live through JobSpy, with country, location, and posting-age filters. Listings without readable descriptions are omitted.
- **Understand the fit:** compare a resume with recognized terms in the job description. The percentage is a keyword-coverage estimate, not an employer's ATS score.
- **Prepare materials:** generate an editable resume and tailored cover letter, review them, and download searchable PDFs. Missing terms stay gaps unless the user supplies evidence they can honestly support.
- **Practice:** review suggested interview questions or use the career coach by text or opt-in voice transcription.
- **Stay organized:** save roles, stages, follow-up dates, and notes in a local tracker, with CSV export.
- **Apply with control:** open the employer's listing after reviewing the packet. AutoApply does not submit applications.

## Quick start on Windows

Use Python 3.12 and PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
streamlit run app.py
```

If PowerShell blocks virtual-environment activation, run the app with `.venv\Scripts\python.exe -m streamlit run app.py` instead.

You can use the app in guest mode. To create AI-assisted drafts, choose Groq or Gemini in the Career Studio sidebar and save that provider key on this device. The key is stored in `.streamlit/secrets.toml`; the app does not bundle or create a key for you.

## Google sign-in

Google sign-in is optional for a local demo; guest mode remains available. To configure OIDC, replace the placeholders in `.streamlit/secrets.toml` with the Google web client values and register these local URLs in the Google Cloud OAuth client:

- Origin: `http://localhost:8501`
- Redirect URI: `http://localhost:8501/oauth2callback`

The consent screen may be in Testing, which limits sign-in to configured test users. A hosted demo needs its own HTTPS origin, redirect URI, and private runtime secrets. Never commit the real `secrets.toml` file.

## Data and privacy

- Resume uploads and generated drafts stay in the current Streamlit session; the app does not save resume files to the local profile or tracker.
- Profile preferences and application tracking are saved under `.streamlit/` on this computer.
- Provider keys are kept in the local ignored `secrets.toml` file when the user chooses to save them. This is local file storage, not a hosted secrets manager.
- AI features send selected resume/job content only after the in-app consent step. Voice transcription has its own consent and explicit Transcribe action.
- The repository includes only `.streamlit/secrets.toml.example`. Do not add real resumes, generated personal documents, local tracker data, API keys, or OAuth secrets to Git.

See [the architecture and privacy notes](docs/architecture-and-privacy.md) for the data flow, and [the demo walkthrough](docs/demo-walkthrough.md) for a short presentation path.

## Project layout

```text
app.py                         Career Studio and app logic
pages/00_Home.py               Home and workflow overview
pages/01_Application_Tracker.py Saved roles and follow-ups
pages/02_Profile.py            Career preferences
pages/03_Settings.py           Provider, privacy, and local-data controls
autoapply_local.py             Local storage helpers, shared theme, navigation
.streamlit/secrets.toml.example Safe configuration template
docs/                           Demo and architecture notes
```

## Current limits

- Live results depend on board availability, country support, and rate limits. LinkedIn and Jobright are not integrated; supported source links are shown when returned by the search provider.
- The keyword scanner recognizes a defined list of terms. Its result does not predict an employer's ATS decision.
- Resume PDF uploads need selectable text. Scanned-image OCR is not included.
- Generated content needs a human review. The app does not verify a user's credentials or guarantee a one-page result for every resume.
- There is no hosted backend or cross-device account database. Local profile/tracker files stay on the machine running Streamlit.

## Before sharing this repository

1. Check `git status` and review every staged file.
2. Confirm that `.streamlit/secrets.toml`, resumes, generated PDFs, tracker data, and OAuth client secrets are excluded.
3. Choose a repository license before inviting others to reuse the code. No license is included yet.
4. For a hackathon submission, follow the current event rules and state accurately what was built during the event, what existed earlier, and how AI tools were used.

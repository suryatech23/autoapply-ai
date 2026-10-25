# Architecture and privacy notes

AutoApply is a local-first Streamlit app. It has no hosted API of its own: the browser connects to the Streamlit process running on the selected computer.

```mermaid
flowchart LR
    U[User in browser] --> UI[Streamlit pages]
    UI -->|Search request| JS[JobSpy]
    JS --> Boards[Supported public job boards]
    Boards -->|Listings and descriptions| UI
    U -->|Resume PDF for this session| PDF[PyMuPDF text extraction]
    PDF --> UI
    UI -->|After in-app consent| AI[Selected Groq or Gemini provider]
    AI -->|Match analysis and drafts| UI
    UI -->|PDF export| OUT[Resume and cover-letter downloads]
    UI --> LOCAL[Local .streamlit profile and tracker files]
    UI -->|Only after voice consent and Transcribe| AI
```

## Where information goes

| Information | Destination | Persistence |
| --- | --- | --- |
| Resume PDF and parsed resume text | Active Streamlit session; selected AI provider after consent for AI features | Not written to the app's profile/tracker files |
| Job search query | JobSpy and the selected external job sources | Depends on those services; searches happen when requested |
| Career preferences and saved roles | `.streamlit/career_profile.json` and `.streamlit/application_tracker.json` | Local files on the app machine |
| AI provider key saved by the user | `.streamlit/secrets.toml` | Local file; ignored by Git |
| Voice recording | Uploaded to the Streamlit process and sent for transcription only after separate consent | App does not write recordings to disk |
| Generated resume/letter | Streamlit session and the user's download location | Not stored as a server-side account document |

## Public demo mode

When the Streamlit Community Cloud deployment sets AUTOAPPLY_PUBLIC_DEMO to true, profile preferences and tracker entries are kept in Streamlit session state instead of shared app files. Those values are temporary and isolated per browser session. Provider keys entered by a visitor are also held only in that session; saving keys to the server filesystem is disabled. Resume uploads and generated drafts remain session data as described above.

The public demo does not include a shared AI provider key. Visitors who choose AI features provide their own key for that session. Keep Google sign-in optional until the hosted redirect URI is configured; the guest path is suitable for a judge demo. This mode reduces cross-visitor data exposure but does not replace a production account database or deployment security review.
## Trust boundaries

- Job descriptions, resumes, and spoken audio are source data, not instructions to the model.
- The matching percentage is based on recognized text terms. It is not an employer's score and does not claim to predict screening outcomes.
- A missing term is not added to a resume unless the user provides supporting evidence and confirms it is accurate.
- The apply action opens an employer page. The user reviews and submits the application there.
- Local `secrets.toml` is convenient for a demo but is not a hosted secrets manager. Keep it private and use deployment-managed secrets for any hosted instance.

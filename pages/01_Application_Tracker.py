import csv
import io
from datetime import date, datetime, timedelta

import streamlit as st

from autoapply_local import app_page_path, apply_theme, load_applications, public_demo_mode, render_nav, save_applications

st.set_page_config(page_title="AutoApply AI · Applications", page_icon="🗂️", layout="wide")
apply_theme(st, hide_sidebar=True)
render_nav(st)
st.markdown('<div class="autoapply-kicker">Stay on top of your search</div>', unsafe_allow_html=True)
st.title("Application tracker")
st.caption("Saved roles, next steps, follow-up dates, and notes stay in this browser session. Resume files are not copied here." if public_demo_mode() else "Saved roles, next steps, follow-up dates, and notes stay on this device in a local file. Resume files are not copied here.")

applications = load_applications()
statuses = ["Saved", "Tailoring", "Ready to apply", "Applied", "Interview", "Offer", "Closed"]
counts = {status: sum(item.get("status", "Saved") == status for item in applications) for status in statuses}
metrics = st.columns(4)
metrics[0].metric("Saved roles", len(applications))
metrics[1].metric("Ready to apply", counts["Ready to apply"])
metrics[2].metric("In interview", counts["Interview"])
metrics[3].metric("Applied", counts["Applied"])

if not applications:
    st.info("Your tracker is ready. Save a role from Career Studio to build your pipeline.")
    st.page_link(app_page_path("app.py"), label="Find roles in Career Studio", icon="⚡")
else:
    search = st.text_input("Filter by role, company, or board", placeholder="Try “intern” or a company name")
    filtered = [item for item in applications if not search or search.casefold() in " ".join(str(item.get(k, "")) for k in ("title", "company", "site")).casefold()]
    st.caption(f"Showing {len(filtered)} of {len(applications)} tracked roles.")
    for item in filtered:
        role_id = str(item.get("id", ""))
        title = str(item.get("title") or "Untitled role")
        company = str(item.get("company") or "Company")
        with st.expander(f"{title} · {company} · {item.get('status', 'Saved')}", expanded=False):
            st.write(f"{item.get('location') or 'Location not listed'} · {str(item.get('site') or 'External').upper()}")
            if str(item.get("url", "")).startswith(("https://", "http://")):
                st.link_button("Open original listing", item["url"])
            date_text = str(item.get("follow_up_date") or "")
            try:
                follow_default = date.fromisoformat(date_text)
            except ValueError:
                follow_default = date.today() + timedelta(days=7)
            form_key = f"tracker_form_{role_id}"
            with st.form(form_key):
                status = st.selectbox("Stage", statuses, index=statuses.index(item.get("status", "Saved")) if item.get("status") in statuses else 0, key=f"status_{role_id}")
                follow_up = st.date_input("Follow-up date", value=follow_default, key=f"followup_{role_id}")
                notes = st.text_area("Private notes", value=str(item.get("notes") or ""), height=100, key=f"notes_{role_id}")
                saved = st.form_submit_button("Save updates")
            if saved:
                updated = []
                for existing in applications:
                    if str(existing.get("id", "")) == role_id:
                        existing = {**existing, "status": status, "follow_up_date": follow_up.isoformat(), "notes": notes, "updated_at": datetime.now().astimezone().isoformat(timespec="seconds")}
                    updated.append(existing)
                save_applications(updated)
                st.success("Tracker updated.")
                st.rerun()
            confirm_remove = st.checkbox("Remove this role from my tracker", key=f"confirm_remove_{role_id}")
            if st.button("Remove role", key=f"remove_{role_id}", disabled=not confirm_remove):
                save_applications([existing for existing in applications if str(existing.get("id", "")) != role_id])
                st.rerun()

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["title", "company", "location", "site", "status", "follow_up_date", "notes", "url"])
    writer.writeheader()
    for item in applications:
        writer.writerow({key: item.get(key, "") for key in writer.fieldnames})
    st.download_button("Download tracker as CSV", output.getvalue().encode("utf-8-sig"), "autoapply_application_tracker.csv", "text/csv")

st.divider()
st.caption(("Application stages and notes stay in this browser session. Nothing is submitted to an employer from the tracker." if public_demo_mode() else "Application stages and notes are stored locally on this computer. Nothing is submitted to an employer from the tracker."))
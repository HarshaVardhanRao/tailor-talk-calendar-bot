import streamlit as st
import requests
import calendar
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="TailorTalk", layout="wide")
st.title("TailorTalk: Book Appointments via Chat")

# Session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "show_form" not in st.session_state:
    st.session_state["show_form"] = False
if "calendar" not in st.session_state:
    st.session_state["calendar"] = []

# Placeholders
chat_placeholder = st.container()
input_placeholder = st.empty()

# ===== Sidebar: Calendar and Appointments =====
def get_blocked_days(events, year, month):
    blocked = set()
    for event in events:
        try:
            start = datetime.fromisoformat(event['start'])
            end = datetime.fromisoformat(event['end'])
            if start.year == year and start.month == month:
                blocked.add(start.day)
            if end.year == year and end.month == month:
                blocked.add(end.day)
        except Exception:
            continue
    return blocked

sidebar = st.sidebar
sidebar.title("📅 My Calendar")
today = datetime.today()
year, month = today.year, today.month
events = st.session_state["calendar"]
blocked_days = get_blocked_days(events, year, month)

# Render calendar
cal = calendar.monthcalendar(year, month)
sidebar.markdown(f"### {calendar.month_name[month]} {year}")
sidebar.markdown("<style>.blocked-day{background:#b6e7a0;border-radius:6px;padding:2px 6px;}</style>", unsafe_allow_html=True)
cal_html = "<table style='width:100%;text-align:center;'>"
cal_html += "<tr>" + "".join(f"<th>{d}</th>" for d in ["Mo","Tu","We","Th","Fr","Sa","Su"]) + "</tr>"
for week in cal:
    cal_html += "<tr>"
    for day in week:
        if day == 0:
            cal_html += "<td></td>"
        elif day in blocked_days:
            cal_html += f"<td class='blocked-day'>{day}</td>"
        else:
            cal_html += f"<td>{day}</td>"
    cal_html += "</tr>"
cal_html += "</table>"
sidebar.markdown(cal_html, unsafe_allow_html=True)

# Appointment List
sidebar.markdown("---")
sidebar.markdown("#### My Appointments")
if not events:
    sidebar.info("No events scheduled.")
else:
    for i, event in enumerate(events, 1):
        sidebar.markdown(f"**{i}. {event['summary']}**<br><span style='font-size:0.9em'>{event['start']} to {event['end']}</span>", unsafe_allow_html=True)

# Sidebar Buttons
sidebar.markdown("---")
if sidebar.button("Book Appointment", key="book_appt_sidebar"):
    st.session_state["show_form"] = True

if sidebar.button("Cancel Appointment", key="cancel_appt_sidebar"):
    st.session_state["messages"].append({"role": "user", "content": "Cancel an appointment"})
    if not events:
        bot_reply = "No appointments to cancel."
    else:
        removed = st.session_state["calendar"].pop()
        bot_reply = f"Cancelled: {removed['summary']} from {removed['start']} to {removed['end']}"
    st.session_state["messages"].append({"role": "bot", "content": bot_reply})


# ===== Main Chat Area =====
st.markdown("<div style='height:60vh; overflow-y:auto; border:1px solid #eee; padding:1em; background:#fafafa;'>", unsafe_allow_html=True)
for msg in st.session_state["messages"]:
    role = "🧑 You" if msg['role'] == "user" else "🤖 Bot"
    st.markdown(f"<p style='margin-bottom:0.5em'><b>{role}:</b> {msg['content']}</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ===== Appointment Booking Modal =====
if st.session_state.get("show_form", False):
    with st.form("book_form", clear_on_submit=True):
        summary = st.text_input("Title", value="Sample Appointment")
        start = st.text_input("Start (YYYY-MM-DDTHH:MM:SS)", value="2025-07-09T10:00:00")
        end = st.text_input("End (YYYY-MM-DDTHH:MM:SS)", value="2025-07-09T11:00:00")
        submitted = st.form_submit_button("Book")
        if submitted:
            st.session_state["messages"].append({"role": "user", "content": f"Book an appointment: {summary} {start} {end}"})
            st.session_state["calendar"].append({"summary": summary, "start": start, "end": end})
            bot_reply = f"Appointment booked: {summary} from {start} to {end}"
            st.session_state["messages"].append({"role": "bot", "content": bot_reply})
            st.session_state["show_form"] = False
    st.button("Cancel", key="cancel_form", on_click=lambda: st.session_state.update({"show_form": False}))

# ===== ChatGPT-style Floating Input Box =====
chat_input_box = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    let textarea = document.querySelector("textarea");
    if (textarea) {
        textarea.addEventListener("keydown", function(e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                document.querySelector("button[type='submit']").click();
            }
        });
    }
});
</script>

<style>
.floating-input-box {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #fff;
    padding: 0.75em 1em;
    border-top: 1px solid #eee;
    box-shadow: 0 -2px 8px rgba(0,0,0,0.04);
    z-index: 1000;
}
</style>
"""

components.html(chat_input_box, height=0)

# Input field at the bottom — just like ChatGPT (no JS)

with input_placeholder:
    with st.form("floating_input_form", clear_on_submit=True):
        user_input = st.text_area(
            label="Message",
            key="input",
            height=100,
            placeholder="Type your message here...",
            label_visibility="collapsed"
        )
        col1, col2 = st.columns([6, 1])
        with col2:
            send = st.form_submit_button("Send", use_container_width=True)

        if send and user_input.strip():
            user_msg = user_input.strip()
            st.session_state["messages"].append({"role": "user", "content": user_msg})

            # --- Intent detection for booking ---
            import re
            booking_keywords = ["book", "schedule", "add appointment", "make appointment", "set meeting", "add event"]
            lower_msg = user_msg.lower()
            is_booking = any(kw in lower_msg for kw in booking_keywords)

            # Try to extract title and datetime info
            title_match = re.search(r"(?:title|about|for) ['\"]?([\w\s]+)['\"]?", user_msg, re.IGNORECASE)
            date_match = re.search(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?)", user_msg)
            all_dates = re.findall(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?)", user_msg)

            # Slot filling state
            if "booking_slots" not in st.session_state:
                st.session_state["booking_slots"] = {}

            if is_booking:
                # Try to fill slots from message
                if title_match:
                    st.session_state["booking_slots"]["summary"] = title_match.group(1).strip()
                if len(all_dates) >= 2:
                    st.session_state["booking_slots"]["start"] = all_dates[0][0]
                    st.session_state["booking_slots"]["end"] = all_dates[1][0]
                elif len(all_dates) == 1:
                    st.session_state["booking_slots"]["start"] = all_dates[0][0]

                # Prompt for missing info
                missing = []
                for slot in ["summary", "start", "end"]:
                    if slot not in st.session_state["booking_slots"]:
                        missing.append(slot)
                if missing:
                    prompts = {
                        "summary": "What is the title of the appointment?",
                        "start": "What is the start date and time? (YYYY-MM-DDTHH:MM:SS)",
                        "end": "What is the end date and time? (YYYY-MM-DDTHH:MM:SS)"
                    }
                    bot_reply = prompts[missing[0]]
                    st.session_state["messages"].append({"role": "bot", "content": bot_reply})
                    st.rerun()
                else:
                    # All info present, add to calendar
                    appt = {
                        "summary": st.session_state["booking_slots"]["summary"],
                        "start": st.session_state["booking_slots"]["start"],
                        "end": st.session_state["booking_slots"]["end"]
                    }
                    st.session_state["calendar"].append(appt)
                    bot_reply = f"Appointment booked: {appt['summary']} from {appt['start']} to {appt['end']}"
                    st.session_state["messages"].append({"role": "bot", "content": bot_reply})
                    st.session_state["booking_slots"] = {}
                    st.rerun()
            elif any(slot in st.session_state.get("booking_slots", {}) for slot in ["summary", "start", "end"]):
                # Continue slot filling
                slots = st.session_state["booking_slots"]
                if "summary" not in slots:
                    slots["summary"] = user_msg
                elif "start" not in slots:
                    slots["start"] = user_msg
                elif "end" not in slots:
                    slots["end"] = user_msg
                # Check if all slots filled
                if all(k in slots for k in ["summary", "start", "end"]):
                    appt = {
                        "summary": slots["summary"],
                        "start": slots["start"],
                        "end": slots["end"]
                    }
                    st.session_state["calendar"].append(appt)
                    bot_reply = f"Appointment booked: {appt['summary']} from {appt['start']} to {appt['end']}"
                    st.session_state["messages"].append({"role": "bot", "content": bot_reply})
                    st.session_state["booking_slots"] = {}
                    st.rerun()
                else:
                    # Ask for next missing slot
                    for slot in ["summary", "start", "end"]:
                        if slot not in slots:
                            prompts = {
                                "summary": "What is the title of the appointment?",
                                "start": "What is the start date and time? (YYYY-MM-DDTHH:MM:SS)",
                                "end": "What is the end date and time? (YYYY-MM-DDTHH:MM:SS)"
                            }
                            bot_reply = prompts[slot]
                            st.session_state["messages"].append({"role": "bot", "content": bot_reply})
                            st.rerun()
            else:
                # Normal chat to backend
                try:
                    resp = requests.post(
                        "https://tailor-talk-calendar-bot.onrender.com/chat",
                        json={"message": user_msg},
                        timeout=10
                    )
                    resp.raise_for_status()
                    bot_reply = resp.json().get("response", "Sorry, no response received.")
                except Exception as e:
                    bot_reply = f"Error: {str(e)}"
                st.session_state["messages"].append({"role": "bot", "content": bot_reply})
                st.rerun()

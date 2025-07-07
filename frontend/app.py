import streamlit as st
import requests

st.title("TailorTalk: Book Appointments via Chat")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

user_input = st.text_input("You:", key="input")

if st.button("Send") and user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    resp = requests.post(
        "http://localhost:8000/chat",
        json={"message": user_input}
    )
    bot_reply = resp.json()["response"]
    st.session_state["messages"].append({"role": "bot", "content": bot_reply})

for msg in st.session_state["messages"]:
    st.write(f"**{msg['role'].capitalize()}:** {msg['content']}")

import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/api/chat"

st.set_page_config(page_title="Doctor’s Assistant", layout="centered")

st.title("🩺 Doctor’s Assistant")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
user_input = st.chat_input("Type your message...")

if user_input:
    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    payload = {
        "message": user_input,
        "session_id": st.session_state.session_id
    }

    response = requests.post(API_URL, json=payload)
    data = response.json()

    # Save session_id
    st.session_state.session_id = data["session_id"]

    # Show bot response
    st.session_state.messages.append(
        {"role": "assistant", "content": data["reply"]}
    )
    with st.chat_message("assistant"):
        st.markdown(data["reply"])

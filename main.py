from flowise import Flowise, PredictionData
import streamlit as st
from streamlit import session_state as state
import streamlit_shadcn_ui as ui
import uuid, json

base_url = st.secrets["BASE_URL"]
flow_id = st.secrets["FLOW_ID"]
api_key = st.secrets["API_KEY"]

client = Flowise(base_url=base_url, api_key=api_key)

if "messages" not in state:
    state.messages = []
if "running" not in state:
    state.running = False
if "prompt" not in state:
    state.prompt = ""
if "sessionId" not in state:
    state.sessionId = ""

def generate_response(prompt):
    state.running = True
    completion = client.create_prediction(
        PredictionData(
            chatflowId=flow_id,
            question=prompt,
            overrideConfig={"sessionId": state.sessionId},
            streaming=True
        )
    )
    for chunk in completion:
        parsed_chunk = json.loads(chunk)
        match parsed_chunk["event"]:
            case "token":
                yield str(parsed_chunk["data"])
            case "end":
                yield ""
                state.running = False


st.title("AcanyBot 🤖")
ui.badges(
    badge_list=[
        ("ArcanicAI", "secondary"), ("QA Chat", "destructive")
    ],
    class_name="flex gap-4"
)

with st.chat_message("assistant"):
    st.write("Chào bạn! Tôi có thể giúp gì?")


for item in state.messages:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])


if not state.running:
    if new_prompt := st.chat_input("Send a message...", disabled=state.running):
        state.prompt = new_prompt
        state.messages.append({"role": "user", "content": new_prompt})
        state.running = True
        with st.chat_message("user"):
            st.write(new_prompt)
        st.rerun()

if state.running:
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response(state.prompt)
            full_response = st.write_stream(response)
                
            bot_data = {
                "role": "assistant",
                "content": full_response
            }
            state.messages.append(bot_data)
            state.prompt = ""
            st.rerun()



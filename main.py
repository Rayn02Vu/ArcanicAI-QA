from flowise import Flowise, PredictionData
import streamlit as st
from streamlit import session_state as state
import streamlit_shadcn_ui as ui
import uuid, json

base_url = st.secrets["BASE_URL"]
flow_id = st.secrets["FLOW_ID"]
api_key = st.secrets["API_KEY"]

client = Flowise(base_url=base_url, api_key=api_key)


def page_setup():
    avatar = "./assets/logo-white.png"
    
    st.set_page_config(
        page_title="Arcanic AI Chatbot",
        page_icon=avatar
    )
    with open("./assets/style.css") as f:
        st.html(f"""<style>{f.read()}</style>""")
    
    
    with st.container(key="center-1"):
        col1, col2 = st.columns([2, 6], gap="medium", vertical_alignment="center")
        with col1:
            st.markdown("<br>", unsafe_allow_html=True)
            st.image("./assets/logo-white.png", width=80)
        with col2:
            st.title("Arcanic AI")
            ui.badges(
                badge_list=[
                    ("Business", "secondary"), 
                    ("Chatbot", "secondary"), 
                    ("QA Chat", "destructive")
                ],
                class_name="flex gap-4"
            )
        
    with st.sidebar:
        st.markdown("""
            <div class="sidebar-container">
                <img src="https://arcanic.ai/wp-content/uploads/2023/11/Arcanic_logo_black-1.png" alt="Logo">
                <h3>Arcanic AI</h3>
            </div>
        """, unsafe_allow_html=True)
            
        st.markdown("*Thúc đẩy đổi mới và phát triển bền vững thông qua các giải pháp ứng dụng trí tuệ nhân tạo.*")
        
        st.markdown("---")
        st.markdown("# Liên hệ")
        st.link_button(
            label="🌐 Website",
            url="https://arcanic.ai",
            type="primary"
        )
        

if "messages" not in state:
    state.messages = []
if "running" not in state:
    state.running = False
if "prompt" not in state:
    state.prompt = ""
if "sessionId" not in state:
    state.sessionId = ""

page_setup()


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
                

with st.chat_message("assistant", avatar="./assets/assistant.png"):
    st.write("Chào bạn! Tôi có thể giúp gì?")


for item in state.messages:
    avatar = None
    if item["role"] == "user":
        avatar = "./assets/user.png"
    if item["role"] == "assistant":
        avatar = "./assets/assistant.png"
    with st.chat_message(item["role"], avatar=avatar):
        st.markdown(item["content"])


if not state.running:
    if new_prompt := st.chat_input("Chat với Bot...", key="chat_input", disabled=state.running):
        state.prompt = new_prompt
        state.messages.append({"role": "user", "content": new_prompt})
        state.running = True
        with st.chat_message("user"):
            st.write(new_prompt)
        st.rerun()

if state.running:
    with st.chat_message("assistant", avatar="./assets/assistant.png"):
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



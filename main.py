from flowise import Flowise, PredictionData
import streamlit as st
from streamlit import session_state as state
import streamlit_shadcn_ui as ui
import uuid, json

base_url = st.secrets["BASE_URL"]
flow_id = st.secrets["FLOW_ID"]
api_key = st.secrets["API_KEY"]

client = Flowise(base_url=base_url, api_key=api_key)

avatar = "./assets/logo-white.png"

st.set_page_config(
    page_title="Arcanic AI Chatbot",
    page_icon=avatar
)
with open("./assets/style.css") as f:
    st.html(f"""<style>{f.read()}</style>""")

    
def sidebar_setup():
    with st.sidebar:
        st.markdown("""
            <div class="sidebar-container">
                <img src="https://arcanic.ai/wp-content/uploads/2023/11/Arcanic_logo_black-1.png" alt="Logo">
                <h2>
                    Arcanic AI
                </h2>
            </div>
        """, unsafe_allow_html=True)
            
        st.markdown("*Thúc đẩy đổi mới và phát triển bền vững thông qua các giải pháp ứng dụng trí tuệ nhân tạo.*")
        
        st.markdown("---")
        st.markdown("# 🌐 Website")
        st.link_button(
            label=":material/home: ArcanicAI",
            url="https://arcanic.ai",
            type="primary",
            use_container_width=True
        )
        st.link_button(
            label=":material/sell: Products",
            url="https://arcanic.ai/arcanic-platform/",
            type="secondary",
            use_container_width=True
        )
        st.link_button(
            label=":material/info: About us",
            url="https://arcanic.ai/about/",
            type="secondary",
            use_container_width=True
        )

        st.markdown("---")
        st.markdown("# 📢 Contact")

        links = f""""""
        for src, url in [
            ("https://img.icons8.com/?size=100&id=8818&format=png&color=000000", "https://www.facebook.com/arcanic.ai.official"), 
            ("https://img.icons8.com/?size=100&id=8808&format=png&color=000000", "https://www.linkedin.com/company/arcanic-ai"),
            ("https://img.icons8.com/?size=100&id=16733&format=png&color=000000", "https://wa.me/+84986962997")
        ]:
            links += f'''
                <a href="{url}">
                    <img src="{src}" width=25/>
                </a>
            '''
        st.markdown(f"""
                <div class="button-row">
                    {links}
                </div>
        """, unsafe_allow_html=True)


with st.container(key="center-1"):
    st.markdown(f"""
        <div class="title">
            <h1>AryanChat</h1>
            <a href="https://arcanic.ai" target="_blank">
                @Sponsored by ArcanicAI
            </a>
        </div>
    """, unsafe_allow_html=True)
        
        
if "messages" not in state:
    state.messages = []
if "running" not in state:
    state.running = False
if "prompt" not in state:
    state.prompt = ""
if "sessionId" not in state:
    state.sessionId = ""


sidebar_setup()


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
                

with st.chat_message("assistant", avatar="./assets/logo-white.png"):
    st.write("Chào bạn! Tôi có thể giúp gì?")


for item in state.messages:
    avatar = None
    if item["role"] == "user":
        avatar = "./assets/user.png"
    if item["role"] == "assistant":
        avatar = "./assets/logo-white.png"
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
    with st.chat_message("assistant", avatar="./assets/logo-white.png"):
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


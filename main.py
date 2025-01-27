"""
Swahili Chat Bot with Consistent Chat Input Layout
"""
import os
import streamlit as st
from dotenv import load_dotenv
from uuid import uuid4

from backend.chat_bot import openai_response_generator, translation_generator, openai_transcribe_audio
from backend.chat_bot import anthropic_response_generator
from frontend.chat import add_chat, delete_chat

anthropic_models = ("claude-3-5-sonnet-latest", "claude-3-5-haiku-latest")
openai_models = ("gpt-4", "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo")
models = openai_models + anthropic_models

load_dotenv()

st.title('Jambo! Nikusaidieje leo? 🙂')
st.caption('Hello! How can I help you today? 🙂')

# Initialize session state variables
if "chats" not in st.session_state:
    st.session_state.chats = {}
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if "prompt" not in st.session_state:
    st.session_state.prompt = ""
if "recording" not in st.session_state:
    st.session_state["recording"] = False
if "audio_submitted" not in st.session_state:
    st.session_state.audio_submitted = False

current_chat_id = st.session_state.current_chat_id
current_chat = st.session_state.chats.get(current_chat_id, None) if current_chat_id else None

# Sidebar elements
with st.sidebar:
    if st.button("New Chat"):
        st.session_state.current_chat_id = None

    openai_api_key = st.text_input(label='OpenAI API Key',
                                   placeholder='your-openai-api-key',
                                   max_chars=200)
    if openai_api_key:
        st.toast("API Key saved successfully!", icon="✅")
    else:
        openai_api_key = os.getenv("OPENAI_API_KEY")

    anthropic_api_key = st.text_input(label="Anthropic API key",
                                      placeholder='your-anthropic-api-key',
                                      max_chars=200)
    if anthropic_api_key:
        st.toast("API Key saved successfully!", icon="✅")
    else:
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    model_choice = st.selectbox("Text Model", models)

    st.markdown("---")
    st.markdown("### Your chats")

    for chat_id in st.session_state.chats:
        colA, colB = st.columns([9, 1])
        with colA:
            chat = st.session_state.chats.get(chat_id)
            chat_button = st.button(
                label=chat["title"],
                use_container_width=True,
                type="secondary" if current_chat_id != chat_id else "primary",
                key=f"chat_{chat_id}"
            )

            if chat_button:
                st.session_state.current_chat_id = chat_id

        with colB:
            delete_button = st.button("🗑️", help="Delete this chat", key=f"delete_{chat_id}")
            if delete_button:
                st.session_state.current_chat_id = None if current_chat_id == chat_id else current_chat_id
                delete_chat(chat_id)
                st.rerun()

# Display chat history
if current_chat:
    current_display_chat = current_chat.get("display")
    for message in current_display_chat:
        role = message['role']
        with st.chat_message(role):
            if role == 'assistant':
                tab_a, tab_b = st.tabs(["Swahili", "English"])
                with tab_a:
                    st.write(message['content']['Swahili'])
                with tab_b:
                    st.write(message['content']['English'])
            else:
                st.write(message['content'])

# Create a container for the input area
input_container = st.container()

# Handle audio recording first


if True:
    col1, col2 = st.columns([1, 9])
    with col1:
        if not st.session_state.recording:
            if st.button("🎤", help="Click to start recording"):
                st.session_state.recording = True
                st.rerun()
        else:
            if st.button("⏺", help="Click to restart recording."):
                st.session_state.recording = False
                st.rerun()

    with col2:
        if st.session_state.recording:
            audio_file = st.audio_input("Record a voice message.")
            if audio_file and not st.session_state.audio_submitted:
                with st.spinner("Converting audio to text..."):
                    try:
                        transcribed_text = openai_transcribe_audio(audio_file, openai_api_key)
                        extracted_text = st.text_area("Transcribed text", transcribed_text)
                        if st.button("Submit"):
                            st.session_state.prompt = extracted_text
                            st.session_state.audio_submitted = True
                            st.session_state.recording = False
                            # Rerun to refresh the UI
                            st.rerun()
                    except Exception as exc:
                        st.error(f"Oops! {exc}!", icon="🚨")
        else:
            user_input = st.chat_input("Say something...")
            if user_input:
                st.session_state.prompt = user_input

with input_container:
    # Handle the prompt processing
    if st.session_state.prompt:
        # Display user message
        with st.chat_message("user"):
            st.markdown(st.session_state.prompt)

        if not current_chat_id:
            chat_id = str(uuid4())
            first_message = st.session_state.prompt
            title = first_message[:20] + ("..." if len(first_message) > 20 else "")
            add_chat(chat_id, title)
            st.rerun()

        # Add user message to currrent chat history
        st.session_state.chats[current_chat_id]["messages"].append({'role': 'user', 'content': st.session_state.prompt})
        st.session_state.chats[current_chat_id]["display"].append({'role': 'user', 'content': st.session_state.prompt})

        updated_messages = st.session_state.chats[current_chat_id].get("messages")

        try:
            # Generate and display response
            with st.chat_message("assistant"):
                tab1, tab2 = st.tabs(["Swahili", "English"])
                with st.spinner('...'):
                    with tab1:
                        if model_choice in openai_models:
                            swahili_response = st.write_stream(
                                openai_response_generator(updated_messages,
                                                          openai_api_key,
                                                          model_choice))
                        else:
                            swahili_response = st.write(
                                anthropic_response_generator(updated_messages,
                                                             anthropic_api_key,
                                                             model_choice))
                    with tab2:
                        english_response = translation_generator(swahili_response)
                        st.markdown(english_response)

            # Add response to chat history
            st.session_state.chats[current_chat_id]["messages"].append({'role': 'assistant', 'content': swahili_response})
            st.session_state.chats[current_chat_id]["display"].append({'role': 'assistant',
                                             'content':
                                             {'Swahili': swahili_response,
                                              'English': english_response}})

            # Reset prompt and audio submission state
            st.session_state.prompt = ""
            st.session_state.audio_submitted = False
            st.rerun()

        except Exception as e:
            st.error(e, icon="🚨")

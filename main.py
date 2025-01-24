"""
Swahili Chat Bot with Consistent Chat Input Layout
"""
import os
import streamlit as st
from dotenv import load_dotenv

from backend.chat_bot import response_generator, translation_generator, transcribe_audio


load_dotenv()

st.title('Jambo! Nikusaidieje leo? 🙂')
st.caption('Hello! How can I help you today? 🙂')

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.display = []
if "prompt" not in st.session_state:
    st.session_state.prompt = ""
if "recording" not in st.session_state:
    st.session_state["recording"] = False
if "audio_submitted" not in st.session_state:
    st.session_state.audio_submitted = False

# Sidebar elements
if st.sidebar.button("New Chat"):
    st.session_state.messages = []
    st.session_state.display = []

if api_key := st.sidebar.text_input(label='API Key', placeholder='your-openai-api-key', key='api_key', max_chars=200):
    st.toast("API Key saved successfully!", icon="✅")
elif not api_key:
    api_key = os.getenv("OPENAI_API_KEY", None)

# Display chat history
for message in st.session_state.display:
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
                if not api_key:
                    st.toast('Please provide an API key.', icon="🚨")
                else:
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
                        transcribed_text = transcribe_audio(audio_file, api_key)
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
        if not api_key:
            st.toast('Please provide an API key.', icon="🚨")
        else:
            # Display user message
            with st.chat_message("user"):
                st.markdown(st.session_state.prompt)

            # Add user message to chat history
            st.session_state.messages.append({'role': 'user', 'content': st.session_state.prompt})
            st.session_state.display.append({'role': 'user', 'content': st.session_state.prompt})

            # Generate and display response
            with st.chat_message("assistant"):
                tab1, tab2 = st.tabs(["Swahili", "English"])
                with st.spinner('...'):
                    with tab1:
                        swahili_response = st.write_stream(response_generator(st.session_state.messages, api_key))
                    with tab2:
                        english_response = translation_generator(swahili_response)
                        st.markdown(english_response)

            # Add response to chat history
            st.session_state.messages.append({'role': 'assistant', 'content': swahili_response})
            st.session_state.display.append({'role': 'assistant', 'content': {'Swahili': swahili_response, 'English': english_response}})

            # Reset prompt and audio submission state
            st.session_state.prompt = ""
            st.session_state.audio_submitted = False

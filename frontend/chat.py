import streamlit as st

def add_chat(chat_id: str, title: str):
    """
    Creates a new chat.
    """
    new_chat = {
        "title": title,
        "messages" : [],
        "display": []
    }
    
    st.session_state.current_chat_id = chat_id
    st.session_state.chats[chat_id] = new_chat

def delete_chat(chat_id: str):
    """
    Deletes a chat.
    """
    deleted_id = st.session_state.chats.pop(chat_id)

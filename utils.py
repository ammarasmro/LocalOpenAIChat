import json
from pathlib import Path
import streamlit as st
from config import CONVERSATIONS_FILE

def save_conversations():
    with open(CONVERSATIONS_FILE, 'w') as f:
        json.dump(st.session_state.conversations, f, indent=2)

def load_conversations():
    if CONVERSATIONS_FILE.exists():
        with open(CONVERSATIONS_FILE, 'r') as f:
            st.session_state.conversations = json.load(f)
            return
    st.session_state.conversations = []

def load_personas(path: Path):
    if not path.exists():
        return []
    personas = json.loads(path.read_text())
    return personas


def save_personas(personas, path: Path):
    with open(path, 'w') as f:
        json.dump(personas, f, indent=2)

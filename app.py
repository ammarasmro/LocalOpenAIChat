import time

import streamlit as st
from openai import OpenAI
from config import *
from utils import load_conversations, save_conversations, load_personas, save_personas

# Remove the hardcoded API key and use the one from config
client = OpenAI(api_key=OPENAI_API_KEY)

# Rest of your current code, but update the paths to use config variables

# Initialize or load conversations
if 'conversations' not in st.session_state:
    load_conversations()

# Initialize or load personas
if 'personas' not in st.session_state:
    st.session_state.personas = load_personas(PERSONAS_PATH)

# Initialize or load selected OpenAI model
if 'model_version' not in st.session_state:
    st.session_state.model_version = "gpt-4o"

# Ensure selected_convo is a valid key from the conversations
if 'selected_convo' not in st.session_state:
    st.session_state.selected_convo = next(iter(st.session_state.conversations), None)

if 'message_text' not in st.session_state:
    st.session_state['message_text'] = ''

if 'current_persona' not in st.session_state:
    st.session_state['current_persona'] = ""

if 'current_persona_name' not in st.session_state:
    st.session_state['current_persona_name'] = ""

def send_message(convo_id, message_text):
    print("Sending message")
    print(message_text)
    if message_text.strip():
        # Append the user's message to the selected conversation
        user_message = {"role": "user", "content": message_text}
        st.session_state.conversations[convo_id].append(user_message)

        # Prepend the system prompt (persona) to the messages
        messages = []
        if st.session_state.current_persona and st.session_state.model_version != "o1-preview":
            system_message = {"role": "system", "content": st.session_state.current_persona}
            messages.append(system_message)
        messages.extend(st.session_state.conversations[convo_id])

        # Send the messages to the OpenAI API
        try:
            print(messages)
            print("Inferencing with model: ", st.session_state.model_version)
            with st.spinner("AI is typing..."):
                completion = client.chat.completions.create(
                    model=st.session_state.model_version,
                    messages=messages
                )
            ai_content = completion.choices[0].message.content.strip()

            # Append the AI's response to the conversation
            ai_message = {
                "role": "assistant",
                "content": ai_content
            }
            st.session_state.conversations[convo_id].append(ai_message)
            print("AI Response:", ai_content)
        except Exception as e:
            st.error(f"An error occurred: {e}")

        # Save the conversations after updating
        save_conversations()
        # Reset the message_text in the state to clear the input box
        st.session_state.message_text = ''


# Sidebar for conversation selection, model selection, and persona management
with st.sidebar:
    st.title("Conversations")

    # Button to create a new conversation
    if st.button("New Conversation"):
        new_convo_id = str(int(time.time()))
        st.session_state.conversations[new_convo_id] = []
        st.session_state.selected_convo = new_convo_id
        save_conversations()

    # New: Rename Conversation
    st.markdown("---")
    st.header("Rename Conversation")
    new_convo_name = st.text_input("New Conversation Name", value=st.session_state.selected_convo)
    if st.button("Rename Conversation"):
        if new_convo_name.strip() == "":
            st.error("Please enter a valid name for the conversation.")
        elif new_convo_name in st.session_state.conversations:
            st.error("A conversation with this name already exists.")
        else:
            st.session_state.conversations[new_convo_name] = st.session_state.conversations.pop(st.session_state.selected_convo)
            st.session_state.selected_convo = new_convo_name
            save_conversations()
            st.success(f"Conversation renamed to '{new_convo_name}' successfully.")

    # Added Conversation Actions
    st.markdown("---")
    st.header("Conversation Actions")

    # Button to save conversation
    if st.button("Save Conversation"):
        save_conversations()
        st.success("Conversation saved successfully.")

    # Button to delete conversation
    if st.button("Delete Conversation"):
        if st.session_state.selected_convo:
            del st.session_state.conversations[st.session_state.selected_convo]
            st.session_state.selected_convo = next(iter(st.session_state.conversations), None) if st.session_state.conversations else None
            save_conversations()
            st.success("Conversation deleted successfully.")
        else:
            st.error("No conversation selected to delete.")

    # Button to clear conversation
    if st.button("Clear Conversation"):
        if st.session_state.selected_convo:
            st.session_state.conversations[st.session_state.selected_convo] = []
            save_conversations()
            st.success("Conversation cleared successfully.")
        else:
            st.error("No conversation selected to clear.")

        # Select box to switch between conversations
    if st.session_state.conversations:
        st.selectbox(
            "Select a Conversation",
            options=list(st.session_state.conversations.keys()),
            format_func=lambda x: f"{x}",
            key="selected_convo"
        )

    st.markdown("---")
    st.header("Model Selection")

    # Selection box to choose the OpenAI model
    available_models = ["gpt-4o", "o1-mini", "o1-preview"]
    selected_model = st.selectbox(
        "Select OpenAI Model",
        options=available_models,
        index=available_models.index(st.session_state.model_version) if st.session_state.model_version in available_models else 0
    )
    st.session_state.model_version = selected_model

    st.markdown("---")
    st.header("Persona Management")

    # Button to create a new persona
    if st.button("New Persona"):
        st.session_state.current_persona = ""
        st.session_state.current_persona_name = ""

    # Selection box to choose a saved persona
    persona_names = [persona['name'] for persona in st.session_state.personas]
    selected_persona = st.selectbox(
        "Select a Persona",
        options=["__Select Persona__"] + persona_names
    )

    if selected_persona != "__Select Persona__":
        # Load the selected persona into the text area and name input
        for persona in st.session_state.personas:
            if persona['name'] == selected_persona:
                st.session_state.current_persona = persona['persona']
                st.session_state.current_persona_name = persona['name']
                break

    # Text area to author/edit the persona
    persona_text = st.text_area(
        "Persona (System Prompt)",
        value=st.session_state.get('current_persona', ''),
        height=200
    )
    st.session_state.current_persona = persona_text

    # Text input for persona name
    persona_name_input = st.text_input(
        "Persona Name",
        value=st.session_state.get('current_persona_name', '')
    )
    st.session_state.current_persona_name = persona_name_input

    # Button to save the persona
    if st.button("Save Persona"):
        if not st.session_state.current_persona_name.strip():
            st.error("Please provide a name for the persona.")
        elif not st.session_state.current_persona.strip():
            st.error("Persona content cannot be empty.")
        else:
            # Check if persona with the same name exists
            existing = next((p for p in st.session_state.personas if p['name'] == st.session_state.current_persona_name), None)
            if existing:
                # Update existing persona
                existing['persona'] = st.session_state.current_persona
                st.success(f"Persona '{st.session_state.current_persona_name}' updated successfully!")
            else:
                # Add new persona
                new_persona = {
                    "name": st.session_state.current_persona_name,
                    "persona": st.session_state.current_persona
                }
                st.session_state.personas.append(new_persona)
                st.success(f"Persona '{st.session_state.current_persona_name}' added successfully!")
            # Save to file
            save_personas(st.session_state.personas, PERSONAS_PATH)

# Main area for the selected conversation
st.title('Local Chatbot')

if st.session_state.selected_convo is not None:
    # User message input at the top
    message = st.chat_input("Input")
    # Send button
    if message:
        send_message(st.session_state.selected_convo, message)

    # Display the selected conversation in reverse order
    if st.session_state.conversations[st.session_state.selected_convo]:
        for message in st.session_state.conversations[st.session_state.selected_convo]:
            role = message["role"]
            content = message["content"]
            with st.chat_message(name=role.capitalize()):
                st.markdown(content)
else:
    st.write("Select or create a conversation to start chatting.")

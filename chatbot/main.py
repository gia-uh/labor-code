import os
from utils.prompting import BASE_PROMPT
from utils.history import Message, TalkHistory
from utils.models import intents
from utils.client import WrappedClient, load_client
import streamlit as st

st.set_page_config(page_title="Asistente del Código de Trabajo")

st.title("Asistente del Anteproyecto del Código de Trabajo")

# Every seen test has its own message history saved
if "ai-messages" not in st.session_state:
    st.session_state["ai-messages"] = TalkHistory(msg_history=[]).model_dump()

conversation: TalkHistory = TalkHistory(**st.session_state["ai-messages"])


def save_history(conversation: TalkHistory):
    st.session_state["ai-messages"] = conversation.model_dump()


def speak(
    ai_client: WrappedClient, conversation: TalkHistory, assistant_name: str, query: str
):
    intent = None
    answer = None

    with st.spinner("Communicating with AI"):
        intent = ai_client.query_classify_intent(TalkHistory.empty(), query)

        if debug_view:
            st.write(f"Intent classified as: {intent.classification}")

    if intent.classification == intents.IntentType.NOT_RELATED:
        answer = "Este asistente únicamente responde a consultas relacionadas con el Anteproyecto del Código de Trabajo. Evite cambiar de tema."

        with st.chat_message(assistant_name):
            st.write(answer)
    else:
        with st.spinner("Communicating with AI"):
            answer = ai_client.query_simple(
                conversation,
                query,
            )

        with st.chat_message(assistant_name):
            answer = st.write_stream(answer)

        conversation.msg_history.append(Message(role="user", content=query))
        conversation.msg_history.append(Message(role="assistant", content=answer))

        save_history(conversation)


ai_client = load_client()

# WATCH: this is a possible change for later
# The name that will be showed in the LLM messages
assistant_name = "ai"

debug_view = False

# WATCH: this should change when getting up production environment
if os.getenv("ENV") == "dev":
    debug_view = st.checkbox("Debug View")

if debug_view:
    st.session_state

left = None
right = None
message_box = None

# Shows debug on the right side with the requests made to the LLM
if debug_view:
    left, right = st.columns([0.6, 0.4])

if debug_view:
    with left:
        message_box = st.container(border=True)
else:
    message_box = st.container(border=True)

user_input = st.chat_input("Di algo")
with message_box:
    for message in conversation.msg_history:
        # WATCH: Change for the username
        with st.chat_message("human" if message.role == "user" else assistant_name):
            st.write(message.content)

# if conversation.msg_history[-1].role == "user":
#     new_conv, message = conversation.detached_message()
#     with message_box:
#         speak(
#             ai_client,
#             new_conv,
#             assistant_name,
#             message.content,
#         )
if user_input:
    with message_box:
        with st.chat_message("human"):
            st.markdown(user_input)

    with message_box:
        speak(
            ai_client,
            conversation,
            assistant_name,
            user_input,
        )

if debug_view:
    with right:
        with st.container():
            for request in ai_client.requests_history:
                with st.expander(f"{request.message}"):
                    st.write("Context:")
                    st.json(
                        [
                            message.model_dump()
                            for message in request.context.msg_history
                        ],
                        expanded=False,
                    )
                    st.write(f"failed: {request.failed}")
                    st.write(f"response: {request.response}")

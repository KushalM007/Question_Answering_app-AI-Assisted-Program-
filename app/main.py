"""Streamlit interface for the AI question-and-answer application."""

import logging

import streamlit as st

from app.config.settings import ConfigurationError, get_settings
from app.services.gemini_service import GeminiQuestionAnsweringService, GeminiServiceError
from app.utils.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="AI Question & Answering System",
    page_icon="💬",
    layout="centered",
)

st.title("AI Question & Answering System")
st.write(
    "Ask a question and get a clear answer from Google Gemini. "
    "Continue the conversation with follow-up questions."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Conversation")
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    try:
        settings = get_settings()
    except ConfigurationError as error:
        st.error(str(error))
        st.caption(
            "The website is running, but answering questions requires a valid "
            "Gemini API key. Keep your key private and never paste it into chat."
        )
        st.stop()

    st.subheader("Model")
    st.caption(settings.model)
    st.caption(f"Temperature: {settings.temperature:g}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask a question")
if question is not None:
    question = question.strip()
    if not question:
        st.warning("Please enter a question before submitting.")
    else:
        user_message = {"role": "user", "content": question}
        conversation = [*st.session_state.messages, user_message]
        with st.chat_message("user"):
            st.markdown(question)

        try:
            service = GeminiQuestionAnsweringService(settings)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = service.generate_answer(conversation)
                st.markdown(answer)
            st.session_state.messages = [
                *conversation,
                {"role": "assistant", "content": answer},
            ]
        except GeminiServiceError as error:
            logger.warning("Question could not be answered (%s).", type(error).__name__)
            st.error(str(error))

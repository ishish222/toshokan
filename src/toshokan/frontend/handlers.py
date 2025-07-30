import gradio as gr
from gradio_agentchatbot_5 import AgentChatbot, ChatMessage
from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    AnyMessage,
)
from toshokan.frontend.helpers import (
    convert_langchain_messages_to_chat_messages,
    convert_chat_messages_to_langchain_messages,
)
from toshokan.frontend.models import models
import pandas as pd


_ = load_dotenv(find_dotenv())


def update_lessons_included_choices(
    lessons_included_in_conversation_drop: gr.Dropdown,
    lessons_df: pd.DataFrame,
):
    choices = lessons_df['Lesson'].tolist()
    return gr.Dropdown(choices=choices, value=[], multiselect=True)


def update_exercise_lesson_dropdown_values(
    lessons_df: pd.DataFrame,
):
    choices = lessons_df['Lesson'].tolist()
    return gr.Dropdown(choices=choices, interactive=True)


def run_the_exercise_chat(
    user_input: str,
    messages: list[AnyMessage],
    config: dict,
):
    model = models[config['model_name']]

    messages = list(convert_chat_messages_to_langchain_messages(messages))

    messages.append(HumanMessage(user_input))
    input_messages = messages

    assistant_message = model.invoke(input_messages)
    messages.append(assistant_message)

    converted_messages = list(convert_langchain_messages_to_chat_messages(messages))

    return converted_messages, ''


def run_the_conversation_chat(
    user_input: str,
    messages: list[AnyMessage],
    config: dict,
):
    model = models[config['model_name']]

    messages = list(convert_chat_messages_to_langchain_messages(messages))

    messages.append(HumanMessage(user_input))
    input_messages = messages

    assistant_message = model.invoke(input_messages)
    messages.append(assistant_message)

    converted_messages = list(convert_langchain_messages_to_chat_messages(messages))

    return converted_messages, ''


def run_the_word_chat(
    user_input: str,
    messages: list[AnyMessage],
    config: dict,
):
    model = models[config['model_name']]
    messages = list(convert_chat_messages_to_langchain_messages(messages))

    messages.append(HumanMessage(user_input))
    input_messages = messages

    assistant_message = model.invoke(input_messages)
    messages.append(assistant_message)

    converted_messages = list(convert_langchain_messages_to_chat_messages(messages))

    return converted_messages, ''


def run_the_aux_chat(
    user_input: str,
    messages: list[AnyMessage],
    config: dict,
):
    model = models[config['model_name']]
    messages = list(convert_chat_messages_to_langchain_messages(messages))

    messages.append(HumanMessage(user_input))
    input_messages = messages

    assistant_message = model.invoke(input_messages)
    messages.append(assistant_message)

    converted_messages = list(convert_langchain_messages_to_chat_messages(messages))

    return converted_messages, ''

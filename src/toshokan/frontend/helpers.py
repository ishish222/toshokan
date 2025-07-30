from gradio_agentchatbot_5 import ChatMessage
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)


def convert_langchain_messages_to_chat_messages(input):
    for msg in input:
        if isinstance(msg, AIMessage):
            yield ChatMessage(role='assistant', content=msg.content)
        elif isinstance(msg, HumanMessage):
            yield ChatMessage(role='user', content=msg.content)
        elif isinstance(msg, SystemMessage):
            continue


def convert_chat_messages_to_langchain_messages(input):
    for msg in input:
        if msg.role == 'assistant':
            yield AIMessage(content=msg.content)
        elif msg.role == 'user':
            yield HumanMessage(content=msg.content)
        elif msg.role == 'system':
            continue

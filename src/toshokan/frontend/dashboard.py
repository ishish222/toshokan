from __future__ import annotations

import os
import gradio as gr
from gradio_agentchatbot_5 import AgentChatbot, ChatMessage
from dotenv import load_dotenv, find_dotenv
from toshokan.frontend.handlers import run_the_aux_chat
from toshokan.frontend.models import models
from toshokan.frontend.config import update_model_name

_ = load_dotenv(find_dotenv())

APP_HOST = os.environ['APP_HOST']
APP_PORT = os.environ['APP_PORT']
COGNITO_DOMAIN = os.environ['COGNITO_DOMAIN']
CLIENT_ID = os.environ['COGNITO_DOMAIN_CLIENT_ID']
REDIRECT_URI_LOGIN = os.environ['COGNITO_DOMAIN_REDIRECT_URI_LOGIN']
REDIRECT_URI_LOGOUT = os.environ['COGNITO_DOMAIN_REDIRECT_URI_LOGOUT']
CODE_VERSION = os.environ['CODE_VERSION']

# Default model
default_model_name = 'openai/gpt-4o'

with gr.Blocks() as dashboard:
    with gr.Row():
        with gr.Column():
            account_label = gr.Label("account", label="Account")
        with gr.Column():
            logout_btn = gr.Button("Logout", link="/logout")

    with gr.Row():
        with gr.Tab("Configuration"):
            current_config = gr.State({
                'model_name': default_model_name,
            })
            model_name_dropdown = gr.Dropdown(
                choices=list(models.keys()),
                value=default_model_name,
                label="Model",
                info="Select the model to use for the conversation",
            )
        with gr.Tab("Library"):
            gr.Label("Exercises")
            gr.Label("Known kanji")
            gr.Label("Scheduled kanji")
        with gr.Tab("Exercises"):
            gr.Label("Exercises")
        with gr.Tab("Conversation"):
            with gr.Tab("Conversation"):
                messages = gr.State({})
                with gr.Row():
                    chat = AgentChatbot()
                with gr.Row():
                    input = gr.Textbox(label="Input")

            with gr.Tab("Japanese word"):
                with gr.Row():
                    word_chat = AgentChatbot()
                with gr.Row():
                    word_input = gr.Textbox(label="Input")

            with gr.Tab("General aux chat"):
                with gr.Row():
                    aux_chat = AgentChatbot()
                with gr.Row():
                    aux_input = gr.Textbox(label="Input")

    model_name_dropdown.select(
        fn=update_model_name,
        inputs=[current_config, model_name_dropdown],
        outputs=current_config,
    )

    aux_input.submit(
        run_the_aux_chat,
        inputs=[aux_input, aux_chat, current_config],
        outputs=[aux_chat, aux_input]
    )

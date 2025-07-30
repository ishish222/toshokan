from __future__ import annotations

import os
import gradio as gr
from gradio_agentchatbot_5 import AgentChatbot, ChatMessage
from dotenv import load_dotenv, find_dotenv
from toshokan.frontend.handlers import (
    run_the_aux_chat,
    run_the_conversation_chat,
    run_the_word_chat,
    run_the_exercise_chat,
)
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
        with gr.Tab("Library"):
            with gr.Accordion("Configuration"):
                current_config = gr.State({
                    'model_name': default_model_name,
                })
                model_name_dropdown = gr.Dropdown(
                    choices=list(models.keys()),
                    value=default_model_name,
                    label="Model",
                    info="Select the model to use for the conversation",
                )
            with gr.Row():
                lessons_df = gr.Dataframe()
                lessons_df_load_btn = gr.Button("Load lessons")
            with gr.Row():
                exercise_types_df = gr.Dataframe()
                exercise_types_df_load_btn = gr.Button("Load exercise types")
            with gr.Row():
                known_kanji_df = gr.Textbox()
                known_kanji_df_load_btn = gr.Button("Load known kanji")
            with gr.Row():
                scheduled_kanji_df = gr.Textbox()
                scheduled_kanji_df_load_btn = gr.Button("Load scheduled kanji")
            with gr.Row():
                lessons_included_in_conversation_df = gr.Dropdown()
                lessons_included_in_conversation_df_load_btn = gr.Button("Load lessons included in conversation")

        with gr.Tab("Exercises"):
            with gr.Accordion("Select lesson and exercise type"):
                with gr.Row():
                    exercise_dropdown = gr.Dropdown(
                        choices=["kanji", "vocabulary", "grammar"],
                        value="kanji",
                        label="Exercise type",
                        info="Select the type of exercise to do",
                    )
                    exercise_type_dropdown = gr.Dropdown(
                        choices=["kanji", "vocabulary", "grammar"],
                        value="kanji",
                        label="Exercise type",
                        info="Select the type of exercise to do",
                    )
            with gr.Row():
                exercise_chat = AgentChatbot()
            with gr.Row():
                exercise_input = gr.Textbox(label="Input")
        with gr.Tab("Conversation"):
            with gr.Tab("Conversation"):
                with gr.Row():
                    conversation_chat = AgentChatbot()
                with gr.Row():
                    conversation_input = gr.Textbox(label="Input")

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

    exercise_input.submit(
        run_the_exercise_chat,
        inputs=[exercise_input, exercise_chat, current_config],
        outputs=[exercise_chat, exercise_input]
    )

    conversation_input.submit(
        run_the_conversation_chat,
        inputs=[conversation_input, conversation_chat, current_config],
        outputs=[conversation_chat, conversation_input]
    )

    word_input.submit(
        run_the_word_chat,
        inputs=[word_input, word_chat, current_config],
        outputs=[word_chat, word_input]
    )

    aux_input.submit(
        run_the_aux_chat,
        inputs=[aux_input, aux_chat, current_config],
        outputs=[aux_chat, aux_input]
    )

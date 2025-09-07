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
    run_the_breakdown_chat,
    update_lessons_included_choices_values,
    update_exercise_lesson_dropdown_values,
    update_exercise_type_dropdown_choices,
    run_the_exercise_initiate,
    run_the_conversation_initiate,
)
from toshokan.frontend.models import reload_models, get_available_model_names
from toshokan.frontend.config import update_model_name, update_openrouter_api_key
from toshokan.frontend.state_manager import (
    load_csv_into_df_lessons,
    load_csv_into_df_exercise_types,
    load_csv_into_df_lessons_selected_for_conversation,
    load_csv_into_txt,
    save_config,
    load_config,
)

_ = load_dotenv(find_dotenv())

COGNITO_INTEGRATE = os.environ.get('COGNITO_INTEGRATE', 'false').lower() == 'true'

if COGNITO_INTEGRATE:
    COGNITO_DOMAIN = os.environ['COGNITO_DOMAIN']
    CLIENT_ID = os.environ['COGNITO_DOMAIN_CLIENT_ID']
    REDIRECT_URI_LOGIN = os.environ['COGNITO_DOMAIN_REDIRECT_URI_LOGIN']
    REDIRECT_URI_LOGOUT = os.environ['COGNITO_DOMAIN_REDIRECT_URI_LOGOUT']

APP_HOST = os.environ['APP_HOST']
APP_PORT = os.environ['APP_PORT']
CODE_VERSION = os.environ['CODE_VERSION']

# Default model
default_model_name = 'openai/gpt-4o'

with gr.Blocks() as dashboard:
    with gr.Row():
        gr.Label("Toshokan (図書館)", show_label=False)

    if COGNITO_INTEGRATE:
        with gr.Row():
            with gr.Column():
                account_label = gr.Label("account", label="Account")
            with gr.Column():
                logout_btn = gr.Button("Logout", link="/logout")

    with gr.Row():
        with gr.Tab("Library"):

            with gr.Accordion("API key"):
                with gr.Row():
                    with gr.Column(scale=9):
                        openrouter_api_key = gr.Textbox(label="Openrouter API key")
                    with gr.Column(scale=1):
                        api_key_save_btn = gr.Button("Save API key")

            with gr.Accordion("Configuration save/load"):
                with gr.Row():
                    with gr.Column():
                        config_load_btn = gr.UploadButton("Load configuration", file_types=[".json"])
                    with gr.Column():
                        config_save_btn = gr.DownloadButton("Save configuration")

            with gr.Accordion("Configuration"):
                runtime_config = gr.State({
                    'model_name': default_model_name,
                    'openrouter_api_key': None,
                })
                model_name_dropdown = gr.Dropdown(
                    choices=get_available_model_names(),
                    value=default_model_name,
                    label="Model",
                    info="Select the model to use for the conversation",
                )
            with gr.Accordion("Lessons"):
                with gr.Row():
                    lessons_df_load_btn = gr.UploadButton("Load lessons", file_types=[".csv"])
                with gr.Row():
                    lessons_df = gr.Dataframe(label="Lessons", headers=["Lesson", "Description"])
            with gr.Accordion("Lessons selected for conversation"):
                with gr.Row():
                    lessons_df_selected_for_conversation_load_btn = gr.UploadButton("Load lessons selected for conversation", file_types=[".csv"])
                with gr.Row():
                    lessons_df_selected_for_conversation = gr.Dataframe(label="Lessons selected for conversation", headers=["Lesson", "Description"])
            with gr.Accordion("Exercise types"):
                with gr.Row():
                    exercise_types_df_load_btn = gr.UploadButton("Load exercise types", file_types=[".csv"])
                with gr.Row():
                    exercise_types_df = gr.Dataframe(label="Exercise types", headers=["Exercise type", "Description"])
            with gr.Accordion("Known kanji"):
                with gr.Row():
                    known_kanji_txt_load_btn = gr.UploadButton("Load known kanji", file_types=[".csv"])
                with gr.Row():
                    known_kanji_txt = gr.Textbox(label="Known kanji")
            with gr.Accordion("Scheduled kanji"):
                with gr.Row():
                    scheduled_kanji_txt_load_btn = gr.UploadButton("Load scheduled kanji", file_types=[".csv"])
                with gr.Row():
                    scheduled_kanji_txt = gr.Textbox(label="Scheduled kanji")

        with gr.Tab("Exercises"):
            with gr.Accordion("Select lesson and exercise type"):
                with gr.Row():
                    lessons_dropdown = gr.Dropdown(label="Lesson")
                    exercise_type_dropdown = gr.Dropdown(label="Exercise type")
                with gr.Row():
                    exercise_initiate_btn = gr.Button("Initiate exercise")

            with gr.Row():
                exercise_chat = AgentChatbot()
            with gr.Row():
                exercise_input = gr.Textbox(label="Input")

        with gr.Tab("Conversation"):
            with gr.Accordion("Lessons included in conversation"):
                # with gr.Row():
                #     lessons_included_in_conversation_drop_load_btn = gr.UploadButton("Load lessons included in conversation", file_types=[".csv"])
                with gr.Row():
                    lessons_included_in_conversation_drop = gr.Dropdown(label="Lessons included in conversation", multiselect=True)
            with gr.Accordion("Formality & situation"):
                with gr.Row():
                    formality_radio = gr.Radio(label="Formality", choices=["Formal", "Semi-formal", "Informal"], value="Semi-formal")
                with gr.Row():
                    conversation_initiate_btn = gr.Button("Initiate conversation")
                with gr.Row():
                    conversation_situation = gr.Textbox(label="Situation", interactive=True, lines=3)
                with gr.Row():
                    conversation_chat = AgentChatbot()
                with gr.Accordion("Notes / kanji", open=False):
                    with gr.Row():
                        conversation_unknown_kanji = gr.Dataframe(label="Unknown kanji", interactive=False)
                    with gr.Row():
                        conversation_notes = gr.Textbox(label="Notes", interactive=False)
                with gr.Row():
                    conversation_input = gr.Textbox(label="Input", lines=3, interactive=True)

        with gr.Tab("Word lookup"):
            with gr.Row():
                word_chat = AgentChatbot()
            with gr.Row():
                word_input = gr.Textbox(label="Input")

        with gr.Tab("Sentence breakdown"):
            with gr.Row():
                breakdown_chat = AgentChatbot()
            with gr.Row():
                breakdown_input = gr.Textbox(label="Input")

        with gr.Tab("General aux chat"):
            with gr.Row():
                aux_chat = AgentChatbot()
            with gr.Row():
                aux_input = gr.Textbox(label="Input")

    model_name_dropdown.select(
        fn=update_model_name,
        inputs=[runtime_config, model_name_dropdown],
        outputs=runtime_config,
    ).then(
        fn=save_config,
        inputs=[runtime_config,
                lessons_df,
                lessons_df_selected_for_conversation,
                exercise_types_df,
                known_kanji_txt,
                scheduled_kanji_txt,
                ],
        outputs=[config_save_btn],
    )

    api_key_save_btn.click(
        fn=update_openrouter_api_key,
        inputs=[runtime_config, openrouter_api_key],
        outputs=[runtime_config, openrouter_api_key],
    )

    lessons_df_load_btn.upload(
        fn=load_csv_into_df_lessons,
        inputs=[lessons_df_load_btn],
        outputs=[lessons_df],
    ).then(
        fn=save_config,
        inputs=[runtime_config,
                lessons_df,
                lessons_df_selected_for_conversation,
                exercise_types_df,
                known_kanji_txt,
                scheduled_kanji_txt,
                ],
        outputs=[config_save_btn],
    )

    lessons_df.change(
        fn=update_lessons_included_choices_values,
        inputs=[lessons_df, lessons_df_selected_for_conversation],
        outputs=[lessons_included_in_conversation_drop],
    ).then(
        fn=update_exercise_lesson_dropdown_values,
        inputs=[lessons_df],
        outputs=[lessons_dropdown],
    ).then(
        fn=save_config,
        inputs=[runtime_config,
                lessons_df,
                lessons_df_selected_for_conversation,
                exercise_types_df,
                known_kanji_txt,
                scheduled_kanji_txt,
                ],
        outputs=[config_save_btn],
    )

    lessons_df_selected_for_conversation_load_btn.upload(
        fn=load_csv_into_df_lessons_selected_for_conversation,
        inputs=[lessons_df_selected_for_conversation_load_btn],
        outputs=[lessons_df_selected_for_conversation],
    ).then(
        fn=save_config,
        inputs=[runtime_config,
                lessons_df,
                lessons_df_selected_for_conversation,
                exercise_types_df,
                known_kanji_txt,
                scheduled_kanji_txt,
                ],
        outputs=[config_save_btn],
    )

    lessons_df_selected_for_conversation.change(
        fn=update_lessons_included_choices_values,
        inputs=[lessons_df, lessons_df_selected_for_conversation],
        outputs=[lessons_included_in_conversation_drop],
    ).then(
        fn=save_config,
        inputs=[runtime_config,
                lessons_df,
                lessons_df_selected_for_conversation,
                exercise_types_df,
                known_kanji_txt,
                scheduled_kanji_txt,
                ],
        outputs=[config_save_btn],
    )

    exercise_types_df_load_btn.upload(
        fn=load_csv_into_df_exercise_types,
        inputs=[exercise_types_df_load_btn],
        outputs=[exercise_types_df],
    ).then(
        fn=update_exercise_type_dropdown_choices,
        inputs=[exercise_types_df],
        outputs=[exercise_type_dropdown],
    ).then(
        fn=save_config,
        inputs=[runtime_config,
                lessons_df,
                lessons_df_selected_for_conversation,
                exercise_types_df,
                known_kanji_txt,
                scheduled_kanji_txt,
                ],
        outputs=[config_save_btn],
    )

    exercise_types_df.change(
        fn=update_exercise_type_dropdown_choices,
        inputs=[exercise_types_df],
        outputs=[exercise_type_dropdown],
    ).then(
        fn=save_config,
        inputs=[runtime_config,
                lessons_df,
                lessons_df_selected_for_conversation,
                exercise_types_df,
                known_kanji_txt,
                scheduled_kanji_txt,
                ],
        outputs=[config_save_btn],
    )

    known_kanji_txt_load_btn.upload(
        fn=load_csv_into_txt,
        inputs=[known_kanji_txt_load_btn],
        outputs=[known_kanji_txt],
    ).then(
        fn=save_config,
        inputs=[runtime_config,
                lessons_df,
                lessons_df_selected_for_conversation,
                exercise_types_df,
                known_kanji_txt,
                scheduled_kanji_txt,
                ],
        outputs=[config_save_btn],
    )

    scheduled_kanji_txt_load_btn.upload(
        fn=load_csv_into_txt,
        inputs=[scheduled_kanji_txt_load_btn],
        outputs=[scheduled_kanji_txt],
    ).then(
        fn=save_config,
        inputs=[runtime_config,
                lessons_df,
                lessons_df_selected_for_conversation,
                exercise_types_df,
                known_kanji_txt,
                scheduled_kanji_txt,
                ],
        outputs=[config_save_btn],
    )

    # recreating the save file
    # this is a hack to mitigate broken downloads

    config_save_btn.click(
        fn=save_config,
        inputs=[runtime_config,
                lessons_df,
                lessons_df_selected_for_conversation,
                exercise_types_df,
                known_kanji_txt,
                scheduled_kanji_txt,
                ],
        outputs=[config_save_btn],
    )

    config_load_btn.upload(
        fn=load_config,
        inputs=[config_load_btn],
        outputs=[
            runtime_config,
            lessons_df,
            lessons_df_selected_for_conversation,
            exercise_types_df,
            known_kanji_txt,
            scheduled_kanji_txt
        ],
    ).then(
        fn=save_config,
        inputs=[runtime_config,
                lessons_df,
                lessons_df_selected_for_conversation,
                exercise_types_df,
                known_kanji_txt,
                scheduled_kanji_txt,
                ],
        outputs=[config_save_btn],
    )

    exercise_initiate_btn.click(
        fn=run_the_exercise_initiate,
        inputs=[
            lessons_dropdown,
            exercise_type_dropdown,
            known_kanji_txt,
            scheduled_kanji_txt,
            exercise_input,
            runtime_config
        ],
        outputs=[exercise_chat, exercise_input]
    )

    exercise_input.submit(
        fn=run_the_exercise_chat,
        inputs=[
            lessons_dropdown,
            exercise_type_dropdown,
            known_kanji_txt,
            scheduled_kanji_txt,
            exercise_input,
            exercise_chat,
            runtime_config
        ],
        outputs=[exercise_chat, exercise_input]
    )

    conversation_initiate_btn.click(
        fn=run_the_conversation_initiate,
        inputs=[formality_radio, runtime_config],
        outputs=[conversation_situation]
    )

    conversation_input.submit(
        run_the_conversation_chat,
        inputs=[
            lessons_included_in_conversation_drop,
            conversation_situation,
            known_kanji_txt,
            scheduled_kanji_txt,
            conversation_input,
            conversation_chat,
            formality_radio,
            runtime_config
        ],
        outputs=[
            conversation_chat,
            conversation_input,
            conversation_notes,
            conversation_unknown_kanji
        ]
    )

    word_input.submit(
        run_the_word_chat,
        inputs=[word_input, word_chat, runtime_config],
        outputs=[word_chat, word_input]
    )

    breakdown_input.submit(
        run_the_breakdown_chat,
        inputs=[breakdown_input, breakdown_chat, runtime_config],
        outputs=[breakdown_chat, breakdown_input]
    )

    aux_input.submit(
        run_the_aux_chat,
        inputs=[aux_input, aux_chat, runtime_config],
        outputs=[aux_chat, aux_input]
    )

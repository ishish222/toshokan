import gradio as gr
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

from toshokan.frontend.prompts.exercise import EXERCISE_SYSTEM_PROMPT
from toshokan.frontend.prompts.conversation import CONVERSATION_SYSTEM_PROMPT, CONVERSATION_SYSTEM_ALL_KANJI_PROMPT, CONVERSATION_SYSTEM_UNKNOWN_KANJI_PROMPT
from toshokan.frontend.schema import ConversationResponse, ConversationKanjiResponse, AllKanji

_ = load_dotenv(find_dotenv())


def update_lessons_included_choices_values(
    lessons_df: pd.DataFrame,
    lessons_df_selected_for_conversation: pd.DataFrame,
):

    names_lessons = lessons_df['Lesson'].tolist()
    names_lessons_selected = lessons_df_selected_for_conversation['Lesson'].tolist()
    descriptions_lessons = lessons_df['Description'].tolist()

    # here we need tuples of (lesson, description) from the DF
    choices = [(lesson, description) for lesson, description in zip(names_lessons, descriptions_lessons)]

    # for values we need to check if the lesson is in the lessons_df_selected_for_conversation
    values = [choice[1] for choice in choices if choice[0] in names_lessons_selected]

    return gr.Dropdown(choices=choices, value=values, multiselect=True)


def update_exercise_lesson_dropdown_values(
    lessons_df: pd.DataFrame,
):
    # here we need tuples of (lesson, description) from the DF
    choices = [(lesson, description) for lesson, description in zip(lessons_df['Lesson'], lessons_df['Description'])]
    return gr.Dropdown(choices=choices, interactive=True)


def update_exercise_type_dropdown_choices(
    exercise_types_df: pd.DataFrame,
):
    # here we need tuples of (exercise_type, description) from the DF
    choices = [(exercise_type, description) for exercise_type, description in zip(exercise_types_df['Exercise Type'], exercise_types_df['Description'])]
    return gr.Dropdown(choices=choices, interactive=True)


def run_the_exercise_initiate(
    lesson: str,
    exercise_type: str,
    known_kanji: str,
    scheduled_kanji: str,
    user_input: str,
    runtime_config: dict,
):

    system_prompt = EXERCISE_SYSTEM_PROMPT.format(
        lesson=lesson,
        exercise_type=exercise_type,
        known_kanji=known_kanji,
        scheduled_kanji=scheduled_kanji
    )

    model = models[runtime_config['model_name']]

    system_message = SystemMessage(content=system_prompt)
    if len(user_input) > 0:
        user_message = HumanMessage(user_input)
        messages = [system_message, user_message]
    else:
        messages = [system_message]

    assistant_message = model.invoke(messages)
    messages = [assistant_message]
    converted_messages = list(convert_langchain_messages_to_chat_messages(messages))

    return converted_messages, ''


def run_the_exercise_chat(
    lesson: str,
    exercise_type: str,
    known_kanji: str,
    scheduled_kanji: str,
    user_input: str,
    messages: list[AnyMessage],
    runtime_config: dict,
):

    if len(messages) == 0:
        # we need to run the initiate exercise
        return run_the_exercise_initiate(
            lesson=lesson,
            exercise_type=exercise_type,
            known_kanji=known_kanji,
            scheduled_kanji=scheduled_kanji,
            user_input=user_input,
            runtime_config=runtime_config)

    else:
        model = models[runtime_config['model_name']]

        messages = list(convert_chat_messages_to_langchain_messages(messages))

        messages.append(HumanMessage(user_input))
        input_messages = messages

        assistant_message = model.invoke(input_messages)
        messages.append(assistant_message)

        converted_messages = list(convert_langchain_messages_to_chat_messages(messages))

        return converted_messages, ''


def detect_all_kanji(
    sentence: str,
    runtime_config: dict,
):
    system_prompt = CONVERSATION_SYSTEM_ALL_KANJI_PROMPT.format(
        sentence=sentence
    )

    model = models[runtime_config['model_name']].with_structured_output(AllKanji)
    system_message = SystemMessage(content=system_prompt)
    messages = [system_message]

    kanji_response = model.invoke(messages)

    return kanji_response.kanji


def detect_unknown_kanji(
    sentence: str,
    known_kanji: str,
    scheduled_kanji: str,
    runtime_config: dict,
):
    unknown_kanji = []

    all_kanji = detect_all_kanji(
        sentence=sentence,
        runtime_config=runtime_config
    )

    if len(all_kanji) > 0:
        for kanji in all_kanji.split(','):
            if kanji in known_kanji or kanji in scheduled_kanji:
                continue
            else:
                unknown_kanji.append(kanji)

    system_prompt = CONVERSATION_SYSTEM_UNKNOWN_KANJI_PROMPT.format(
        kanji=unknown_kanji
    )
    model = models[runtime_config['model_name']].with_structured_output(ConversationKanjiResponse)
    system_message = SystemMessage(content=system_prompt)
    messages = [system_message]

    kanji_response = model.invoke(messages)

    records = [
        {
            'Kanji': k.kanji,
            'Hiragana': k.hiragana,
            'Explanation': k.explanation,
        }
        for k in kanji_response.unknown_kanji
    ]

    if not records:
        return pd.DataFrame(columns=['Kanji', 'Hiragana', 'Explanation'])

    return pd.DataFrame.from_records(records)


def run_the_conversation_initiate(
    lessons: str,
    known_kanji: str,
    scheduled_kanji: str,
    user_input: str,
    runtime_config: dict,
):
    system_prompt = CONVERSATION_SYSTEM_PROMPT.format(
        lessons=lessons,
        known_kanji=known_kanji,
        scheduled_kanji=scheduled_kanji
    )

    model = models[runtime_config['model_name']].with_structured_output(ConversationResponse)

    system_message = SystemMessage(content=system_prompt)
    if len(user_input) > 0:
        user_message = HumanMessage(user_input)
        messages = [system_message, user_message]
    else:
        messages = [system_message]

    conversation_response = model.invoke(messages)
    messages = [AIMessage(conversation_response.response)]

    converted_messages = list(convert_langchain_messages_to_chat_messages(messages))

    unknown_kanji = detect_unknown_kanji(
        sentence=conversation_response.response,
        known_kanji=known_kanji,
        scheduled_kanji=scheduled_kanji,
        runtime_config=runtime_config
    )

    return converted_messages, '', conversation_response.notes, unknown_kanji


def run_the_conversation_chat(
    lessons: str,
    known_kanji: str,
    scheduled_kanji: str,
    user_input: str,
    messages: list[AnyMessage],
    runtime_config: dict,
):
    # import pdb; pdb.set_trace()

    if len(messages) == 0:
        # we need to run the initiate conversation
        return run_the_conversation_initiate(
            lessons=lessons,
            known_kanji=known_kanji,
            scheduled_kanji=scheduled_kanji,
            user_input=user_input,
            runtime_config=runtime_config)
    else:
        model = models[runtime_config['model_name']].with_structured_output(ConversationResponse)

        messages = list(convert_chat_messages_to_langchain_messages(messages))

        messages.append(HumanMessage(user_input))
        input_messages = messages

        conversation_response = model.invoke(input_messages)
        messages.append(AIMessage(conversation_response.response))

        converted_messages = list(convert_langchain_messages_to_chat_messages(messages))

        unknown_kanji = detect_unknown_kanji(
                sentence=conversation_response.response,
                known_kanji=known_kanji,
                scheduled_kanji=scheduled_kanji,
                runtime_config=runtime_config
            )

        return converted_messages, '', conversation_response.notes, unknown_kanji


def run_the_word_chat(
    user_input: str,
    messages: list[AnyMessage],
    runtime_config: dict,
):
    model = models[runtime_config['model_name']]
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
    runtime_config: dict,
):
    model = models[runtime_config['model_name']]
    messages = list(convert_chat_messages_to_langchain_messages(messages))

    messages.append(HumanMessage(user_input))
    input_messages = messages

    assistant_message = model.invoke(input_messages)
    messages.append(assistant_message)

    converted_messages = list(convert_langchain_messages_to_chat_messages(messages))

    return converted_messages, ''

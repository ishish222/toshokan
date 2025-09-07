import random
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
from toshokan.frontend.models import reload_models, ensure_openrouter_api_key
import pandas as pd

from toshokan.frontend.prompts.breakdown import BREAKDOWN_SYSTEM_PROMPT
from toshokan.frontend.prompts.exercise import EXERCISE_SYSTEM_PROMPT
from toshokan.frontend.prompts.conversation import (
    CONVERSATION_SYSTEM_PROMPT,
    CONVERSATION_SYSTEM_ALL_KANJI_PROMPT,
    CONVERSATION_SYSTEM_UNKNOWN_KANJI_PROMPT,
    CONVERSATION_SYSTEM_INITIALIZE_PROMPT,
)
from toshokan.frontend.prompts.word import WORD_SYSTEM_PROMPT
from toshokan.frontend.prompts.aux import AUX_SYSTEM_PROMPT
from toshokan.frontend.schema import ConversationResponse, ConversationKanjiResponse, AllKanji, ConversationSituation

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

    model = reload_models()[runtime_config['model_name']]

    if not ensure_openrouter_api_key(model):
        raise gr.Error('Openrouter API key is not set')

    system_prompt = EXERCISE_SYSTEM_PROMPT.format(
        lesson=lesson,
        exercise_type=exercise_type,
        known_kanji=known_kanji,
        scheduled_kanji=scheduled_kanji
    )

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
        model = reload_models()[runtime_config['model_name']]

        if not ensure_openrouter_api_key(model):
            raise gr.Error('Openrouter API key is not set')

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
    runtime_config: dict,
):
    model = reload_models()[runtime_config['model_name']]

    if not ensure_openrouter_api_key(model):
        raise gr.Error('Openrouter API key is not set')

    system_prompt = WORD_SYSTEM_PROMPT.format(
        word=user_input
    )
    system_message = SystemMessage(content=system_prompt)

    messages = [system_message] + list(convert_chat_messages_to_langchain_messages(messages)) + [HumanMessage(user_input)]

    assistant_message = model.invoke(messages)
    messages.append(assistant_message)

    converted_messages = list(convert_langchain_messages_to_chat_messages(messages))

    return converted_messages, ''


def run_the_breakdown_chat(
    user_input: str,
    messages: list[AnyMessage],
    runtime_config: dict,
):
    model = reload_models()[runtime_config['model_name']]

    if not ensure_openrouter_api_key(model):
        raise gr.Error('Openrouter API key is not set')

    system_prompt = BREAKDOWN_SYSTEM_PROMPT.format(
        sentence=user_input
    )
    system_message = SystemMessage(content=system_prompt)

    messages = [system_message] + list(convert_chat_messages_to_langchain_messages(messages)) + [HumanMessage(user_input)]

    assistant_message = model.invoke(messages)
    messages.append(assistant_message)

    converted_messages = list(convert_langchain_messages_to_chat_messages(messages))

    return converted_messages, ''


def run_the_aux_chat(
    user_input: str,
    messages: list[AnyMessage],
    runtime_config: dict,
):
    model = reload_models()[runtime_config['model_name']]

    if not ensure_openrouter_api_key(model):
        raise gr.Error('Openrouter API key is not set')

    system_prompt = AUX_SYSTEM_PROMPT.format(
        user_input=user_input
    )
    system_message = SystemMessage(content=system_prompt)

    messages = [system_message] + list(convert_chat_messages_to_langchain_messages(messages)) + [HumanMessage(user_input)]

    assistant_message = model.invoke(messages)
    messages.append(assistant_message)

    converted_messages = list(convert_langchain_messages_to_chat_messages(messages))

    return converted_messages, ''


def detect_all_kanji(
    sentence: str,
    runtime_config: dict,
):
    model = reload_models()[runtime_config['model_name']]

    if not ensure_openrouter_api_key(model):
        raise gr.Error('Openrouter API key is not set')

    system_prompt = CONVERSATION_SYSTEM_ALL_KANJI_PROMPT.format(
        sentence=sentence
    )

    model = model.with_structured_output(AllKanji)
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
    model = reload_models()[runtime_config['model_name']]

    if not ensure_openrouter_api_key(model):
        raise gr.Error('Openrouter API key is not set')

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
    model = model.with_structured_output(ConversationKanjiResponse)
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
    formality: str,
    runtime_config: dict,
):
    model = reload_models()[runtime_config['model_name']]

    if not ensure_openrouter_api_key(model):
        raise gr.Error('Openrouter API key is not set')

    system_prompt = CONVERSATION_SYSTEM_INITIALIZE_PROMPT.format(
        formality=formality
    )

    system_message = SystemMessage(content=system_prompt)
    messages = [system_message]

    model = model.with_structured_output(ConversationSituation)

    seed = random.randint(0, 2**31-1)
    # import pdb; pdb.set_trace()

    conversation_situation = model.invoke(messages, seed=seed)

    return conversation_situation.situation


def run_the_conversation_chat(
    lessons: str,
    situation: str,
    known_kanji: str,
    scheduled_kanji: str,
    user_input: str,
    messages: list[AnyMessage],
    formality: str,
    runtime_config: dict,
):
    model = reload_models()[runtime_config['model_name']]

    if not ensure_openrouter_api_key(model):
        raise gr.Error('Openrouter API key is not set')

    system_prompt = CONVERSATION_SYSTEM_PROMPT.format(
        lessons=lessons,
        situation=situation,
        known_kanji=known_kanji,
        scheduled_kanji=scheduled_kanji,
        formality=formality
    )

    model = model.with_structured_output(ConversationResponse)

    system_message = SystemMessage(content=system_prompt)

    messages = list(convert_chat_messages_to_langchain_messages(messages))

    if len(user_input) > 0:
        user_message = HumanMessage(user_input)
        messages = [system_message] + messages + [user_message]
    else:
        messages = [system_message] + messages

    conversation_response = model.invoke(messages)
    messages.append(AIMessage(conversation_response.response))

    converted_messages = list(convert_langchain_messages_to_chat_messages(messages))

    unknown_kanji = detect_unknown_kanji(
            sentence=conversation_response.response,
            known_kanji=known_kanji,
            scheduled_kanji=scheduled_kanji,
            runtime_config=runtime_config
        )

    return converted_messages, '', conversation_response.notes, unknown_kanji

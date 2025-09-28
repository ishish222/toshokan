from typing import Optional
import json
import pandas as pd
import gradio as gr
from gradio_agentchatbot_5 import ChatMessage


# df conversion helpers

def _serialize_chat_message(chat_message: ChatMessage) -> dict:
    """Convert a ChatMessage object to a serializable dictionary."""
    return {
        'role': chat_message.role,
        'content': chat_message.content,
        'metadata': getattr(chat_message, 'metadata', {})
    }


def _deserialize_chat_message(data: dict) -> ChatMessage:
    """Convert a dictionary back to a ChatMessage object."""
    return ChatMessage(
        role=data['role'],
        content=data['content'],
        metadata=data.get('metadata', {})
    )


def _serialize_chat_data(chat_data) -> list[dict]:
    """Convert chat data (list of ChatMessage objects) to serializable format."""
    if not chat_data:
        return []
    serialized = []
    for message in chat_data:
        if isinstance(message, ChatMessage):
            serialized.append(_serialize_chat_message(message))
        else:
            # If it's already a dict or other serializable format
            serialized.append(message)
    return serialized


def _deserialize_chat_data(serialized_data: list[dict]) -> list[ChatMessage]:
    """Convert serialized chat data back to ChatMessage objects."""
    if not serialized_data:
        return []
    chat_messages = []
    for item in serialized_data:
        if isinstance(item, dict) and 'role' in item and 'content' in item:
            chat_messages.append(_deserialize_chat_message(item))
        else:
            # Handle case where data might already be ChatMessage objects
            chat_messages.append(item)
    return chat_messages


def _df_to_records(df: Optional[pd.DataFrame]) -> list[dict]:
    """Safely convert a DataFrame to a list-of-dicts records representation.

    Returns an empty list if *df* is ``None`` or empty.
    """
    if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
        return df.to_dict(orient="records")
    return []


def _records_to_df(records: list[dict]) -> pd.DataFrame:
    """Convert a list of dicts into a DataFrame – returns an empty DF for
    falsy/empty input so callers can always rely on getting a DataFrame.
    """
    return pd.DataFrame(records or [])


def load_csv_into_df_lessons(
    lessons_file_path: str,
):
    columns = ['Lesson', 'Description']
    lessons_df = pd.read_csv(lessons_file_path, names=columns)
    return lessons_df


def load_csv_into_df_lessons_selected_for_conversation(
    lessons_selected_for_conversation_file_path: str,
):
    columns = ['Lesson']
    lessons_selected_for_conversation_df = pd.read_csv(lessons_selected_for_conversation_file_path, names=columns)
    return lessons_selected_for_conversation_df


def load_csv_into_df_exercise_types(
    exercise_types_file_path: str,
):
    columns = ['Exercise Type', 'Description']
    exercise_types_df = pd.read_csv(exercise_types_file_path, names=columns)
    return exercise_types_df


def load_csv_into_txt(
    lessons_file_path: str,
):
    with open(lessons_file_path, 'r') as file:
        return file.read()


def save_config(
    config: dict,
    lessons_df: pd.DataFrame,
    lessons_df_selected_for_conversation: pd.DataFrame,
    exercise_types_df: pd.DataFrame,
    known_kanji_txt: str,
    scheduled_kanji_txt: str,
) -> gr.DownloadButton:

    config['lessons_df'] = _df_to_records(lessons_df)
    config['lessons_df_selected_for_conversation'] = _df_to_records(lessons_df_selected_for_conversation)
    config['exercise_types_df'] = _df_to_records(exercise_types_df)
    config['known_kanji_txt'] = known_kanji_txt
    config['scheduled_kanji_txt'] = scheduled_kanji_txt

    # save config to json file in /tmp/
    with open('/tmp/toshokan_config.json', 'w') as file:
        json.dump(config, file)

    return gr.DownloadButton(
        value='/tmp/toshokan_config.json'
    )


def load_config(
    config_file_path: str,
) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame, str, str]:
    with open(config_file_path, 'r') as file:
        config = json.load(file)

    lessons_df = _records_to_df(config['lessons_df'])
    lessons_df_selected_for_conversation = _records_to_df(config['lessons_df_selected_for_conversation'])
    exercise_types_df = _records_to_df(config['exercise_types_df'])
    known_kanji_txt = config['known_kanji_txt']
    scheduled_kanji_txt = config['scheduled_kanji_txt']

    return config, lessons_df, lessons_df_selected_for_conversation, exercise_types_df, known_kanji_txt, scheduled_kanji_txt


def exercise_chat_to_state(
    lessons_dropdown: list[str],
    exercise_type_dropdown: gr.Dropdown,
    exercise_chat: gr.Chatbot,
    exercise_state: dict,
):
    position_str = f"{'_'.join(lessons_dropdown)}_{exercise_type_dropdown}"

    exercise_state[position_str] = exercise_chat

    return exercise_state


def exercise_state_to_chat(
    lessons_dropdown: list[str],
    exercise_type_dropdown: gr.Dropdown,
    exercise_state: dict,
):
    position_str = f"{'_'.join(lessons_dropdown)}_{exercise_type_dropdown}"
    if position_str not in exercise_state:
        return []

    exercise_chat = exercise_state[position_str]

    return exercise_chat


def save_exercise_progress(
    exercise_state: dict,
):
    # Serialize the exercise_state to handle ChatMessage objects
    serialized_state = {}
    for key, value in exercise_state.items():
        if isinstance(value, list):
            # Check if it's a list of ChatMessage objects
            serialized_state[key] = _serialize_chat_data(value)
        else:
            serialized_state[key] = value

    # save exercise_chat to json file in /tmp/
    with open('/tmp/toshokan_exercise_progress.json', 'w') as file:
        json.dump(serialized_state, file)

    return gr.DownloadButton(
        value='/tmp/toshokan_exercise_progress.json'
    )


def load_exercise_progress(
    exercise_progress_path_file: str,
):
    with open(exercise_progress_path_file, 'r') as file:
        serialized_state = json.load(file)

    # Deserialize the state to restore ChatMessage objects
    exercise_state = {}
    for key, value in serialized_state.items():
        if isinstance(value, list):
            # Check if it's serialized chat data and deserialize it
            exercise_state[key] = _deserialize_chat_data(value)
        else:
            exercise_state[key] = value

    return exercise_state

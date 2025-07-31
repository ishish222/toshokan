from typing import Optional
import json
import pandas as pd
import gradio as gr


# df conversion helpers

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

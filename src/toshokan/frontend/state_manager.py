import gradio as gr
import pandas as pd


def load_csv_into_df_lessons(
    lessons_file_path: str,
):
    columns = ['Lesson', 'Description']
    lessons_df = pd.read_csv(lessons_file_path, names=columns)
    return lessons_df


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

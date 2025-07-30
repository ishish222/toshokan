import gradio as gr
import pandas as pd


def load_csv_into_df(
    lessons_file_path: gr.UploadButton,
):
    columns = ['Lesson', 'Description']
    lessons_df = pd.read_csv(lessons_file_path, names=columns)
    return lessons_df


def load_csv_into_txt(
    lessons_file_path: gr.UploadButton,
):
    with open(lessons_file_path, 'r') as file:
        return file.read()

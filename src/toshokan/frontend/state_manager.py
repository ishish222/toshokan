import gradio as gr
import pandas as pd


def load_csv_into_df(
    lessons_file_path: gr.UploadButton,
):
    columns = ['Lesson', 'Description']
    lessons_df = pd.read_csv(lessons_file_path, names=columns)
    return lessons_df

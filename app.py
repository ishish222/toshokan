import os
import gradio as gr
from dotenv import load_dotenv

# Load environment variables if .env file exists
load_dotenv()

# Set default environment variables for HF Spaces
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('APP_HOST', '0.0.0.0')
os.environ.setdefault('APP_PORT', '7860')
os.environ.setdefault('COGNITO_INTEGRATE', 'false')

# Detect if running on HF Spaces
if 'SPACE_ID' in os.environ:
    # Running on HF Spaces
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['COGNITO_INTEGRATE'] = 'false'

# Import the dashboard after setting environment variables
from src.toshokan.frontend.dashboard import dashboard

# Launch the Gradio app
if __name__ == "__main__":
    dashboard.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        favicon_path="src/static/favicon.ico"
    )

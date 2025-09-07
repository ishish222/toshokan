from pydantic import SecretStr
from typing import Optional
import os
from langchain_openai import ChatOpenAI


class ChatOpenRouter(ChatOpenAI):
    def __init__(self,
                 model_name: str,
                 openai_api_key: Optional[SecretStr] = None,
                 openai_api_base: str = 'https://openrouter.ai/api/v1',
                 **kwargs):
        # Set a dummy API key if none provided to avoid validation errors
        # The actual key will be set when the model is used
        if openai_api_key is None:
            openai_api_key = SecretStr("dummy-key-for-initialization")
        
        super().__init__(openai_api_base=openai_api_base,
                         api_key=openai_api_key,
                         model_name=model_name, **kwargs)

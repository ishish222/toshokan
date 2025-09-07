from .openrouter import ChatOpenRouter
import os


def ensure_openrouter_api_key(
    model: ChatOpenRouter
) -> bool:
    return os.environ.get('OPENROUTER_API_KEY') is not None


def get_available_model_names():
    """Return just the model names for dropdown without initializing models"""
    return [
        'anthropic/claude-3.5-sonnet',
        'anthropic/claude-3-opus', 
        'ai21/jamba-1-5-large',
        'google/gemini-pro-1.5',
        'openai/gpt-4o-2024-11-20',
        'openai/gpt-4o',
        'openai/gpt-4o (0.7)',
        'openai/gpt-4o-mini-2024-07-18',
        'openai/o3-mini',
        'meta-llama/llama-3.1-70b-instruct',
        'meta-llama/llama-3.1-405b-instruct',
        'deepseek/deepseek-chat',
        'mistralai/mixtral-8x22b-instruct',
        'mistralai/mistral-large',
        'qwen/qwen-turbo'
    ]


def reload_models():
    models = {}

    # Always use the current environment variable value
    api_key = os.environ.get('OPENROUTER_API_KEY')

    models['anthropic/claude-3.5-sonnet'] = ChatOpenRouter(
        model_name='anthropic/claude-3.5-sonnet',
        temperature=0.0,
        openai_api_key=api_key,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'anthropic/claude-3.5-sonnet'
        }
    )
    models['anthropic/claude-3-opus'] = ChatOpenRouter(
        model_name='anthropic/claude-3-opus',
        temperature=0.0,
        openai_api_key=api_key,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'anthropic/claude-3-opus'
        }
    )

    models['ai21/jamba-1-5-large'] = ChatOpenRouter(
        model_name='ai21/jamba-1-5-large',
        temperature=0.0,
        openai_api_key=api_key,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'ai21/jamba-1-5-large'
        }
    )

    models['google/gemini-pro-1.5'] = ChatOpenRouter(
        model_name='google/gemini-pro-1.5',
        temperature=0.0,
        openai_api_key=api_key,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'google/gemini-pro-1.5'
        }
    )

    models['openai/gpt-4o-2024-11-20'] = ChatOpenRouter(
        model_name='openai/gpt-4o-2024-11-20',
        temperature=0.0,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'openai/gpt-4o-2024-11-20'
        }
    )

    models['openai/gpt-4o'] = ChatOpenRouter(
        model_name='openai/gpt-4o',
        temperature=0.0,
        openai_api_key=api_key,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'openai/gpt-4o'
        }
    )

    models['openai/gpt-4o (0.7)'] = ChatOpenRouter(
        model_name='openai/gpt-4o',
        temperature=0.7,
        openai_api_key=api_key,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'openai/gpt-4o'
        }
    )
    models['openai/gpt-4o-mini-2024-07-18'] = ChatOpenRouter(
        model_name='openai/gpt-4o-mini-2024-07-18',
        temperature=0.0,
        openai_api_key=api_key,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'openai/gpt-4o-mini-2024-07-18'
        }
    )

    models['openai/o3-mini'] = ChatOpenRouter(
        model_name='openai/o3-mini',
        temperature=0.0,
        openai_api_key=api_key,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'openai/o3-mini'
        }
    )

    models['openai/gpt-4o-mini-2024-07-18'] = ChatOpenRouter(
        model_name='openai/gpt-4o-mini-2024-07-18',
        temperature=0.0,
        openai_api_key=api_key,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'openai/gpt-4o-2024-08-06'
        }
    )

    models['meta-llama/llama-3.1-70b-instruct'] = ChatOpenRouter(
        model_name='meta-llama/llama-3.1-70b-instruct',
        temperature=0.0,
        openai_api_key=api_key,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'meta-llama/llama-3.1-70b-instruct'
        }
    )

    models['meta-llama/llama-3.1-405b-instruct'] = ChatOpenRouter(
        model_name='meta-llama/llama-3.1-405b-instruct',
        temperature=0.0,
        openai_api_key=api_key,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'meta-llama/llama-3.1-405b-instruct'
        }
    )

    models['deepseek/deepseek-chat'] = ChatOpenRouter(
        model_name='deepseek/deepseek-chat',
        temperature=0.0,
        openai_api_key=api_key,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'deepseek/deepseek-chat'
        }
    )

    models['mistralai/mixtral-8x22b-instruct'] = ChatOpenRouter(
        model_name='mistralai/mixtral-8x22b-instruct',
        temperature=0.0,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'mistralai/mixtral-8x22b-instruct'
        }
    )

    models['mistralai/mistral-large'] = ChatOpenRouter(
        model_name='mistralai/mistral-large',
        temperature=0.0,
        openai_api_key=api_key,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'mistralai/mistral-large'
        }
    )

    models['qwen/qwen-turbo'] = ChatOpenRouter(
        model_name='qwen/qwen-turbo',
        temperature=0.0,
        openai_api_key=api_key,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'qwen/qwen-turbo'
        }
    )

    models['deepseek/deepseek-chat'] = ChatOpenRouter(
        model_name='deepseek/deepseek-chat',
        temperature=0.0,
        openai_api_key=api_key,
        metadata={
            'ls_provider': 'openrouter',
            'ls_model_name': 'deepseek/deepseek-chat'
        }
    )

    return models

import os


def update_model_name(
        config: dict,
        model_name: str,
) -> dict:
    config['model_name'] = model_name
    return config


def update_openrouter_api_key(
        config: dict,
        openrouter_api_key: str,
) -> tuple[dict, str]:
    config['openrouter_api_key'] = openrouter_api_key
    os.environ['OPENROUTER_API_KEY'] = openrouter_api_key
    return config, ''

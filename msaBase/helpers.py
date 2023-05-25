import os
from typing import Any, Dict, List, Union

from dotenv import load_dotenv
from msaDocModels.sdu import SDUPage


def convert_list_to_str(input_list: List) -> str:
    """
    Converts list of string to one string

    Parameters:
        input_list: list of strings
    Returns:
        A single string joined from the input_list by whitespace
    """
    return " ".join(input_list)


def convert_dict_to_str(input_dict: Dict[Any, str]) -> str:
    """
    Converts dict values to one string

    Parameters:
        input_dict: dict with strings for values
    Returns:
        A single string joined from the input_dict values by whitespace"""
    return "\n".join(input_dict.values())


def get_one_string_text(input_text: Union[str, List[str], Dict[Any, str]]):
    """
    Check type input and return one string

    Parameters:
        input_text: string, list of strings, or dict with strings for values
    Returns:
        A single string
    """
    type_input_text = type(input_text)
    if type_input_text == str:
        input_text = input_text
    elif type_input_text == list:
        input_text = convert_list_to_str(input_list=input_text)
    elif type_input_text == dict:
        input_text = convert_dict_to_str(input_dict=input_text)
    return input_text.replace("/n", " ").replace('"', "'")


async def get_all_sentences(text_pages: List[SDUPage]) -> Dict[int, List[str]]:
    """
    Extracts all sentences from a list of text pages.

    Parameters:

        text_pages: A list of SDUPage objects representing text pages.

    Returns:

        A dictionary where the keys are page IDs and the values are lists of sentences from the corresponding page.
    """
    sentences: Dict[int, List[str]] = {}
    for page in text_pages:
        sentences[page.id] = []
        for par in page.text.paragraphs:
            for sen in par.sentences:
                sentences[page.id].append(sen.text)
    return sentences


def _prioritize_envs_in_settings(prefix: str) -> dict[str, Any]:
    """
    Helper function to fix an issue where config.json overwrites .env variables with specified prefix
    in Config child class of Pydantic's settings

    Args:
        prefix: A string value from inner Config class of a pydantic model. Example:
        ```
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            env_prefix = "msa_app_"
        ```
        to dynamically retrieve the env_prefix: `MSAServiceDefinition().Config().env_prefix`

    Returns:
        map of the env variables which will overwrite values provided in config.json file
    """
    load_dotenv()
    envs: list[str] = os.environ
    envs_map = {}
    for env in envs:
        if env.startswith(prefix):
            env_with_prefix_key: str = env
            env_key = env_with_prefix_key.replace(prefix, "")
            envs_map[env_key] = os.environ.get(env)
    return envs_map

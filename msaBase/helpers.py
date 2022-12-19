from typing import Any, Dict, List, Union


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

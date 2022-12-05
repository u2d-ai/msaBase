def convert_list_to_str(input_list: list) -> str:
    """Convert list of string to one string"""
    return " ".join(input_list)


def convert_dict_to_str(input_dict: dict) -> str:
    """Converting dict values to one string"""
    return "\n".join(input_dict.values())


def get_one_string_text(input_text):
    """Check type input and return one string"""
    type_input_text = type(input_text)
    if type_input_text == str:
        input_text = input_text
    elif type_input_text == list:
        input_text = convert_list_to_str(input_list=input_text)
    elif type_input_text == dict:
        input_text = convert_dict_to_str(input_dict=input_text)
    return input_text

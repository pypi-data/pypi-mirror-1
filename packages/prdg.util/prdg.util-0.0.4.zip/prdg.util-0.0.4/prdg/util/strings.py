from re import findall

FORMAT_KEY_PATTERN = r'%\((\S+)\)\S'


def get_formatting_keys(template_str):
    """
    Get the formatting keys from an string. Formatting keys are strings like
    '%(some_key)s, used with the % operator.
    """
    return findall(FORMAT_KEY_PATTERN, template_str)

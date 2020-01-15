"""
    Additional functions to work with urls
"""
from typing import Dict
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode


PARAMS_INDEX = 4


def add_url_parameters(url: str, parameters: Dict[str, str]) -> str:
    """
        Adds new parameters to url
    Args:
        url: original url
        parameters: dict with params

    Returns: New url
    """

    parsed_url = list(urlparse(url))

    extended_url_parameters = dict(parse_qsl(parsed_url[PARAMS_INDEX]))
    extended_url_parameters.update(parameters)

    parsed_url[PARAMS_INDEX] = urlencode(extended_url_parameters, doseq=True)

    return urlunparse(parsed_url)

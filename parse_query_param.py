def parse_query_param(url, param):
    """Parses the query string of a URL and returns the value of a parameter.
    Args:
        url: A URL.
        param: A string representing the name of the parameter.
    Returns:
        The value of the parameter.
    """

    try:
        return parse.parse_qs(parse.urlparse(url).query)[param][0]
    except:
        return None

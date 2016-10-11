def matchall(text, patterns):
    """Scans through a string for substrings matched some patterns.
    Args:
        text: A string to be scanned.
        patterns: a list of regex pattern.
    Returns:
        a list if matched. empty if not.
    """

    ret = []
    for pattern in patterns:
        match = re.findall(pattern, text)
        ret += match

    return ret

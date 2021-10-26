def normalize(string: str):
    """
    Normalize the value of the provided utf8 encoded string.
    """
    return string.decode("utf8").strip("\n")

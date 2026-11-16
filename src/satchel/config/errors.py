class ConfigError(Exception):
    """A problem with the user's configuration.

    The message is written for the user and is shown to them as it is, so it
    should say what is wrong and where, without a traceback being needed.
    """

class InstagramBaseError(Exception):
    """
    Raise for instagram specific kind of exception
    """
    pass


class InstagramRequestError(InstagramBaseError):
    """
    Raise for errors due to HTTP(S) requests
    """
    pass


class InstagramAuthError(InstagramBaseError):
    """
    Raise for errors due to authentication
    """
    pass

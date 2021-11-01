import ast
import base64
from .errors import *


class InstagramSession:
    def __init__(self):
        self.cookie = dict()

    def get_cookie(self):
        cookie = dict()
        for k, v in self.cookie.items():
            cookie[k] = v
        return cookie

    def set_cookie(self, cookie):
        if self.is_valid_cookie(cookie):
            self.cookie = cookie.copy()

    def get_cookie_param(self, param):
        if param in self.cookie.keys():
            return self.cookie[param]
        else:
            raise KeyError(f"Parameter {param} not set in cookie")

    def get_session_str(self):
        """
        get current session as a string
        """
        b64s = base64.b64encode(str(self.cookie).encode("utf-8"))
        return b64s.decode("utf-8")

    def set_session_str(self, session_str):
        """
        sets session string
        """
        dstr = base64.b64decode(session_str.encode("utf-8"))
        cookie = ast.literal_eval(dstr.decode("utf-8"))
        self.set_cookie(cookie)

    @staticmethod
    def is_valid_cookie(cookie):
        additional_info = ""
        try:
            if "csrftoken" in cookie.keys() and "sessionid" in cookie.keys():
                return True
        except Exception as e:
            additional_info = " Additional Info: " + str(e)
            pass
        raise InstagramAuthError("Invalid cookie provided." + additional_info)


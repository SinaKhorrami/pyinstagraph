import requests
from .errors import *

USER_AGENT = "Mozilla/5.0 (Windows NT 5.1; rv:52.0) Gecko/20100101 Firefox/52.0"


class InstagramNetworkAdapter:
    def __init__(self, session, proxy=None):
        self.headers = {}
        self.session = session
        self.proxy = proxy

    def get(self, url, xhr=False, json_resp=True, setcookie=False):
        self._reset_base_headers()
        req = None
        if not xhr:
            try:
                req = requests.get(url, headers=self.headers, cookies=self.session.cookie)
            except Exception as e:
                error_info = f"Additional Info: {e}"
        else:
            self._add_complementary_headers()
            try:
                req = requests.get(url, headers=self.headers, cookies=self.session.cookie)
            except Exception as e:
                error_info = f"Additional Info: {e}"
        if req:
            if setcookie:
                self.session.set_cookie(req.cookies)
            if json_resp:
                return req.json()
            else:
                return req.text
        else:
            raise InstagramRequestError(error_info)

    def post(self, url, data, xhr=True, json_resp=True, setcookie=False):
        self._reset_base_headers()
        req = None
        if not xhr:
            try:
                req = requests.post(url, data=data, headers=self.headers, cookies=self.session.cookie)
            except Exception as e:
                error_info = f"Additional Info: {e}"
        else:
            self._add_complementary_headers()
            try:
                req = requests.post(url, data=data, headers=self.headers, cookies=self.session.cookie)
            except Exception as e:
                error_info = f"Additional Info: {e}"
        if req:
            if setcookie:
                self.session.set_cookie(req.cookies)
            if json_resp:
                return req.json()
            else:
                return req.text
        else:
            raise InstagramRequestError(error_info)

    def get_html(self, url, xhr=False, setcookie=False):
        return self.get(url, xhr=xhr, setcookie=setcookie, json_resp=False)

    def _reset_base_headers(self):
        self.headers = {
            'User-Agent': USER_AGENT,
            'Accept': '*/*',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
            'Referer': 'https://www.instagram.com',
        }

    def _add_complementary_headers(self, csrftoken):
        self.headers.update({
            'x-csrftoken': csrftoken,
            'x-requested-with': 'XMLHttpRequest',
            'Authority': 'www.instagram.com',
            'Origin': 'https://www.instagram.com',
            'Content-Type': 'application/x-www-form-urlencoded'
        })


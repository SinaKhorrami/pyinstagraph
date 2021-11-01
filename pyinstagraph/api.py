import re
import json
import datetime
from .urls import InstagramURL
from .network import InstagramNetworkAdapter
from .session import InstagramSession
from .errors import *


class Instagraph:
    def __init__(self, username=None, password=None, cookie=None, session_str=None):
        if not username and not cookie and not session_str:
            raise ValueError("At least one form of authentication should be provided: "
                             "user/pass, session or cookie")
        self.username = username
        self.password = password
        self.session = InstagramSession()
        self.net = InstagramNetworkAdapter(session=self.session)
        self.logger = print
        # authentication
        if cookie:
            self.session.set_cookie(cookie)
        elif session_str:
            self.session.set_session_str(session_str)
        else:
            self._login()
        self.logged_in = self._is_logged_in()

    def _login(self):
        if not self.logged_in:
            # first visit
            csrftoken = self._get_csrftoken()
            if not csrftoken:
                return False
            # login attempt
            try:
                json_resp = self.net.post(InstagramURL.LOGIN.value,
                                          data=self._make_login_payload(),
                                          setcookie=True)
                if json_resp["authenticated"]:
                    self._log("Login Successful")
                    return True
                else:
                    self._log(f"Login Failed")
                    return False
            except Exception as e:
                self._log(e)
                return False

    def _get_csrftoken(self):
        try:
            first_request = self.net.get(InstagramURL.MAIN.value, setcookie=True)
            return self.session.get_cookie_param("csrftoken")
        except Exception as e:
            self._log(e)
            return None

    def _is_logged_in(self):
        try:
            probe_request = self.net.get_html(InstagramURL.MAIN.value)
            html = re.findall("<html.+?class\s?=\s?[\"'](.+?)[\"'].?>", probe_request, re.IGNORECASE)
            if len(html) > 0:
                if "not-logged-in" in html[0]:
                    return False
                else:
                    return True
        except Exception as e:
            self._log(e)
            return False

    def _log(self, msg):
        self.logger(msg)

    def _make_login_payload(self):
        now = int(datetime.datetime.now().timestamp())
        payload = {
            'username': self.username,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{now}:{self.password}',
            'queryParams': {},
            'optIntoOneTap': 'false'
        }
        return payload

    def _load_feed(self, url):
        """
        Loads a JSON feed from instagram.com endpoint url
        """
        try:
            return self.net.get(url)
        except Exception as e:
            self._log(e)
            return dict()

    def _load_page_data(self, url):
        """
        Loads JSON data embedded into instagram.com HTML pages
        """
        try:
            page_request = self.net.get_html(url)
            # extract shared data from JS
            shared_data_raw = re.findall("<script.+?>window._sharedData[ ]?=[ ]?(.+?);</script>",
                                         page_request)
            return json.loads(shared_data_raw[0])
        except Exception as e:
            self._log(e)
            return dict()

    def get_timeline_feed(self):
        return self._load_feed(self.generate_timeline_url(cursor=None))

    def get_posts_from_timeline(self, no_posts=50):
        """
        Fetches minimum of no_posts from current logged-in user timeline
        """
        posts = []
        has_next_page = True
        cursor = None
        while len(posts) < no_posts and has_next_page:
            feed = self._load_feed(self.generate_timeline_url(cursor=cursor))
            timeline = feed["data"]["user"]["edge_web_feed_timeline"]
            has_next_page, cursor, post_edges = self.extract_posts_from_timeline(timeline)
            posts += post_edges
        return posts

    def _resolve_user_id(self, user):
        user_page_data = self._load_page_data(InstagramURL.MAIN.value + user)
        return user_page_data['entry_data']['ProfilePage'][0]['graphql']['user']['id']

    def get_posts_from_user(self, user, no_posts=50):
        """
        Fetches minimum of no_posts from username
        """
        user_id = self._resolve_user_id(user)
        return self.get_posts_from_user_id(user_id, no_posts=no_posts)

    def get_posts_from_user_id(self, user_id, no_posts=50):
        """
        Fetches minimum of no_posts from user_id
        """
        posts = []
        has_next_page = True
        cursor = None
        while len(posts) < no_posts and has_next_page:
            feed = self._load_feed(self.generate_userfeed_url(user_id, cursor))
            timeline = feed["data"]["user"]["edge_owner_to_timeline_media"]
            has_next_page, cursor, post_edges = self.extract_posts_from_timeline(timeline)
            posts += post_edges
        return posts

    def get_user_feed(self, user_id):
        """
        Get user's feed by id.
        """
        return self._load_feed(self.generate_userfeed_url(user_id))

    @staticmethod
    def extract_posts_from_timeline(timeline):
        try:
            has_next_page = timeline["page_info"]["has_next_page"]
            end_cursor = timeline["page_info"]["end_cursor"]
            posts = []
            for edge in timeline['edges']:
                posts.append(edge)
            return has_next_page, end_cursor, posts
        except Exception as e:
            return False, None, []

    @staticmethod
    def generate_timeline_url(cursor=None):
        if cursor:
            cursor.replace("=", "%3D")
            return f'{InstagramURL.TIMELINE.value}&variables=%7B%22cached_feed_item_ids%22%3A%5B%5D%2C' \
                   f'%22fetch_media_item_count%22%3A12%2C' \
                   f'%22fetch_media_item_cursor%22%3A%22{cursor}%22%2C' \
                   f'%22fetch_comment_count%22%3A4%2C' \
                   f'%22fetch_like%22%3A3%2C' \
                   f'%22has_stories%22%3Afalse%2C' \
                   f'%22has_threaded_comments%22%3Atrue%7D'
        else:
            return f'{InstagramURL.TIMELINE.value}&variables=%7B%22cached_feed_item_ids%22%3A[]%2C' \
                   f'%22fetch_media_item_count%22%3A12%2C' \
                   f'%22fetch_comment_count%22%3A4%2C' \
                   f'%22fetch_like%22%3A3%2C' \
                   f'%22has_stories%22%3Afalse%2C' \
                   f'%22has_threaded_comments%22%3Atrue%7D'

    @staticmethod
    def generate_userfeed_url(user_id, cursor=None):
        if cursor:
            cursor.replace("=", "%3D")
            return f'{InstagramURL.USERFEED.value}&variables=%7B%22id%22%3A%22{user_id}%22%2C' \
                   f'%22first%22%3A30%2C' \
                   f'%22after%22%3A%22{cursor}%22%7D'
        else:
            return f'{InstagramURL.USERFEED.value}&variables=%7B%22id%22%3A%22{user_id}%22%2C' \
                   f'%22first%22%3A30%7D'

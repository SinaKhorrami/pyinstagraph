import enum


class InstagramURL(enum.Enum):
    MAIN = "https://instagram.com/"
    LOGIN = "https://instagram.com/accounts/login/ajax/"
    SIGNUP = "https://www.instagram.com/accounts/web_create_ajax/attempt/"
    TIMELINE = "https://www.instagram.com/graphql/query/?query_hash=dbdfd83895d23a4a0b0f68a85486e91c"
    USERFEED = "https://www.instagram.com/graphql/query/?query_hash=8c2a529969ee035a5063f2fc8602a0fd"
from cgi import parse_qs
from urllib import urlencode
from urllib2 import HTTPError, URLError
from urlparse import urlsplit, urlunsplit

from django.conf import settings
from django.utils.functional import update_wrapper


try:
    from oauthtwitter import OAuthApi
except AttributeError:
    # oauthtwitter has a nasty bug, where it imports oauth incorrectly.
    import oauth
    import oauth.oauth
    oauth.__dict__.update((k, v) for k, v in oauth.oauth.__dict__.iteritems()
                          if not (k.startswith('__') and k.endswith('__')))
    from oauthtwitter import OAuthApi


def TwitterApi(token=None):
    """
    Returns an OAuthApi object, given an optional `token`.
    """
    # Use the default consumer key and secret from settings.
    return OAuthApi(consumer_key=settings.TWITTER_CONSUMER_KEY,
                    consumer_secret=settings.TWITTER_CONSUMER_SECRET,
                    access_token=token)


def fail_whale(f):
    MAX_TRIES = 3
    def wrapper(*args, **kwargs):
        for tries in range(MAX_TRIES - 1):
            try:
                return f(*args, **kwargs)
            except HTTPError, e:
                if e.code != 503:
                    # Retry when Service Temporarily Unavailable
                    raise
            except URLError, e:
                errno = getattr(e.reason, 'args', [None])[0]
                if errno != 8:
                    # Retry when EOF occurred in violation of protocol
                    raise
        return f(*args, **kwargs)
    return update_wrapper(wrapper, f)

@fail_whale
def get_user_info(access_token):
    return TwitterApi(access_token).GetUserInfo()

def update_qs(url, dictionary):
    s, n, p, query, f = urlsplit(str(url))
    query_dict = parse_qs(query)
    query_dict.update(dictionary)
    return urlunsplit((s, n, p, urlencode(query_dict), f))

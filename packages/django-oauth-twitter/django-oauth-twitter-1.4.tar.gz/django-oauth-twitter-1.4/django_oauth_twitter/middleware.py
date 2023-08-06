from django.utils.functional import curry, SimpleLazyObject

from django_oauth_twitter import ACCESS_KEY, REQUEST_KEY, USERINFO_KEY
from django_oauth_twitter.utils import get_user_info

from oauth.oauth import OAuthToken
import simplejson
import twitter


class SessionMiddleware(object):
    def process_request(self, request):
        """Import the Twitter token from the Session into the Request."""
        request.twitter_access_token = None
        request.twitter_request_token = None
        request.twitter_userinfo = None
        if ACCESS_KEY in request.session:
            token_str = request.session[ACCESS_KEY]
            token = OAuthToken.from_string(token_str)
            request.twitter_access_token = token
            userinfo = SimpleLazyObject(curry(cached_user_info,
                                              request, token))
            request.twitter_userinfo = userinfo
        if REQUEST_KEY in request.session:
            token_str = request.session[REQUEST_KEY]
            request.twitter_request_token = OAuthToken.from_string(token_str)


def cached_user_info(request, token):
    userinfo = None
    try:
        userinfo = get_user_info(token)
    except:
        pass
    if userinfo is None:
        # Look for a cached copy in the session
        if USERINFO_KEY in request.session:
            userinfo_dict = simplejson.loads(request.session[USERINFO_KEY])
            userinfo = twitter.User.NewFromJsonDict(userinfo_dict)
    else:
        request.session[USERINFO_KEY] = userinfo.AsJsonString()
    return userinfo

def remove_tokens(request):
    if ACCESS_KEY in request.session:
        del request.session[ACCESS_KEY]
        request.twitter_access_token = None
    if REQUEST_KEY in request.session:
        del request.session[REQUEST_KEY]
        request.twitter_request_token = None
    if USERINFO_KEY in request.session:
        del request.session[USERINFO_KEY]
        request.twitter_userinfo = None

def set_access_token(request, access_token):
    request.session[ACCESS_KEY] = access_token.to_string()
    request.twitter_access_token = access_token

def set_request_token(request, request_token):
    request.session[REQUEST_KEY] = request_token.to_string()
    request.twitter_request_token = request_token

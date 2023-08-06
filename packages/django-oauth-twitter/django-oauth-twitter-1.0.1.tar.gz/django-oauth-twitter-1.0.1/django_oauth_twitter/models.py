from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from oauth.oauth import OAuthToken
import simplejson
import twitter

from django_oauth_twitter.utils import get_user_info


class TwitterUserManager(models.Manager):
    @staticmethod
    def _access_token(access_token, userinfo=None):
        if userinfo is None:
            userinfo = get_user_info(access_token)
        attributes = {'access_token_str': access_token,
                      'twitter_id': userinfo.id,
                      'userinfo_json': userinfo.AsJsonString()}
        return (attributes, userinfo)

    def create_twitter_user(self, user, access_token, userinfo=None):
        """
        Returns a new TwitterUser from `user` and `access_token`.

        If `userinfo` is provided, it will use that instead of
        fetching recent Twitter user info using `access_token`.
        """
        attributes, userinfo = self._access_token(access_token, userinfo)
        return self.create(user=user, **attributes)

    def update_or_create(self, user, access_token, userinfo=None):
        """
        Returns a (TwitterUser, created) tuple from `user` and `access_token`.

        `created` is True when the TwitterUser had to be created.

        If `userinfo` is provided, it will use that instead of
        fetching recent Twitter user info using `access_token`.
        """
        attributes, userinfo = self._access_token(access_token, userinfo)
        obj, created = self.get_or_create(user=user,
                                          defaults=attributes)
        if not created:
            save = False
            if obj.update_access_token(access_token):
                save = True
            if obj.update_userinfo(userinfo):
                save = True
            if save:
                obj.save()
        user._twitter_cache = obj
        return obj, created


class TwitterUser(models.Model):
    user = models.OneToOneField(User, unique=True, verbose_name=_('user'),
                                related_name='twitter')
    twitter_id = models.IntegerField(unique=True)
    access_token_str = models.TextField()
    userinfo_json = models.TextField(blank=True)
    objects = TwitterUserManager()

    def __unicode__(self):
        return self.userinfo().screen_name

    def get_access_token(self):
        if self.access_token_str:
            return OAuthToken.from_string(self.access_token_str)
        return None

    def set_access_token(self, value):
        if hasattr(value, 'to_string'):
            self.access_token_str = value.to_string()
        else:
            self.access_token_str = value

    access_token = property(get_access_token, set_access_token)

    def update_access_token(self, access_token):
        if self.access_token != access_token:
            self.access_token = access_token
            return True

    def userinfo(self):
        if self.userinfo_json:
            userinfo_dict = simplejson.loads(self.userinfo_json)
            userinfo = twitter.User.NewFromJsonDict(userinfo_dict)
        else:
            userinfo = self.update_userinfo()
        return userinfo

    def update_userinfo(self, userinfo=None):
        if userinfo is None:
            userinfo = get_user_info(self.access_token)
        userinfo_json = userinfo.AsJsonString()
        if self.userinfo_json != userinfo_json:
            self.userinfo_json = userinfo_json
            return userinfo

    def get_screen_name(self):
        return self.userinfo().screen_name
    
    screen_name = property(get_screen_name)

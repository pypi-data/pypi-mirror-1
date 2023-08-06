from __future__ import with_statement

import os

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase
from django.core.urlresolvers import NoReverseMatch, reverse

from mocker import Mocker, ANY, MATCH

from oauth.oauth import OAuthToken

from django_oauth_twitter import ACCESS_KEY, REQUEST_KEY, USERINFO_KEY
from django_oauth_twitter.middleware import (cached_user_info,
                                             set_access_token,
                                             set_request_token)
from django_oauth_twitter.models import TwitterUser
from django_oauth_twitter.test_urls import oauthtwitter
from django_oauth_twitter.views import LazyReverse, OAuthTwitter
from django_oauth_twitter.utils import TwitterApi, get_user_info

TOKEN = OAuthToken.from_string('oauth_token=a&oauth_token_secret=b')


class MiddlewareTest(TestCase):
    def setUp(self):
        self.mocker = Mocker()

    def test_set_access_token(self):
        request = self.mocker.mock()
        request.session[ACCESS_KEY] = TOKEN.to_string()
        request.twitter_access_token = TOKEN
        with self.mocker:
            set_access_token(request, TOKEN)

    def test_set_request_token(self):
        request = self.mocker.mock()
        request.session[REQUEST_KEY] = TOKEN.to_string()
        request.twitter_request_token = TOKEN
        with self.mocker:
            set_request_token(request, TOKEN)


class UtilsTest(TestCase):
    def setUp(self):
        settings.TWITTER_CONSUMER_KEY = 'KEY'
        settings.TWITTER_CONSUMER_SECRET = 'SECRET'
        self.mocker = Mocker()

    def test_twitter_api(self):
        from oauthtwitter import OAuthApi
        self.assertTrue(isinstance(TwitterApi(), OAuthApi))
        self.assertTrue(isinstance(TwitterApi(token=''), OAuthApi))

    def test_get_user_info(self):
        Api = self.mocker.replace(TwitterApi)
        Api(TOKEN).GetUserInfo()
        self.mocker.result('GetUserInfo')
        with self.mocker:
            self.assertEqual(get_user_info(TOKEN), 'GetUserInfo')


class LazyReverseTest(TestCase):
    urls = 'django_oauth_twitter.test_urls'

    def test_str(self):
        self.assertEqual(str(LazyReverse('http://google.com/')),
                         'http://google.com/')
        self.assertEqual(str(LazyReverse('/home/')), '/home/')
        self.assertEqual(str(LazyReverse('home')), '/home/')
        self.assertRaises(NoReverseMatch, str, LazyReverse('unknown'))
        self.assertEqual(str(LazyReverse(oauthtwitter.register)),
                         '/twitter/register/')


class OAuthTwitterTest(TestCase):
    urls = 'django_oauth_twitter.test_urls'

    def setUp(self):
        self.mocker = Mocker()
        self.password = User.objects.create_user('password', '', 'password')
        self.twitter = User.objects.create_user('twitter', '', 'twitter')
        json = '{"screen_name": "twitter"}'
        self.twitter_user = TwitterUser.objects.create(user=self.twitter,
                                                       twitter_id=1,
                                                       userinfo_json=json)
        self.old_template_dirs = settings.TEMPLATE_DIRS
        settings.TEMPLATE_DIRS = (os.path.join(__file__, 'templates'),)

    def tearDown(self):
        settings.TEMPLATE_DIRS = self.old_template_dirs

    def test_association_user_add(self):
        # User adds association.
        self.assertRaises(TwitterUser.DoesNotExist,
                          TwitterUser.objects.get, user=self.password)
        self.assertTrue(self.client.login(username=self.password.username,
                                          password=self.password.username))
        Api = self.mocker.replace(TwitterApi)
        Api(ANY).getAccessToken()
        self.mocker.result(TOKEN)
        userinfo = self.mocker.mock()
        userinfo.id
        self.mocker.result('2')
        userinfo.AsJsonString()
        self.mocker.result('{}')
        self.mocker.count(1, 2)
        Api(ANY).GetUserInfo()
        self.mocker.result(userinfo)
        with self.mocker:
            # User goes off to Twitter and gets redirected back to callback
            session = self.client.session
            session[REQUEST_KEY] = TOKEN.to_string()
            session.save()
            response = self.client.get(reverse(oauthtwitter.callback),
                                       {'oauth_token': TOKEN.key},
                                       follow=True)
            self.assertEqual(response.redirect_chain,
                [('http://testserver/twitter/associate/?associated=1', 302),
                 ('http://testserver/twitter/associate/', 302)]
            )
            self.assertEqual(response.status_code, 200)

    def test_association_user_remove(self):
        # User removes association.
        self.assertRaises(TwitterUser.DoesNotExist,
                          TwitterUser.objects.get, user=self.password)
        self.assertTrue(self.client.login(username=self.password.username,
                                          password=self.password.username))
        response = self.client.post(reverse(oauthtwitter.associate),
                                    {'action': 'remove',
                                     'twitter_id': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertRaises(TwitterUser.DoesNotExist,
                          TwitterUser.objects.get, user=self.password)
        response = self.client.post(reverse(oauthtwitter.associate))
        self.assertEqual(response.status_code, 200)
        self.assertRaises(TwitterUser.DoesNotExist,
                          TwitterUser.objects.get, user=self.password)

    def test_association_associated_add(self):
        # Associated adds association.
        self.assertTrue(self.twitter.twitter)
        self.assertTrue(self.client.login(username=self.twitter.username,
                                          password=self.twitter.username))
        Api = self.mocker.replace(TwitterApi)
        Api(ANY).getAccessToken()
        self.mocker.result(TOKEN)
        userinfo = self.mocker.mock()
        userinfo.id
        self.mocker.result('2')
        userinfo.AsJsonString()
        self.mocker.result('{}')
        self.mocker.count(1, 2)
        Api(ANY).GetUserInfo()
        self.mocker.result(userinfo)
        with self.mocker:
            # User goes off to Twitter and gets redirected back to callback
            session = self.client.session
            session[REQUEST_KEY] = TOKEN.to_string()
            session.save()
            response = self.client.get(reverse(oauthtwitter.callback),
                                       {'oauth_token': TOKEN.key})
            self.assertEqual(response['Location'],
                             'http://testserver/twitter/associate/')

    def test_association_associated_remove(self):
        # Associated removes association.
        self.assertTrue(self.twitter.twitter)
        self.assertTrue(self.client.login(username=self.twitter.username,
                                          password=self.twitter.username))
        response = self.client.post(reverse(oauthtwitter.associate))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(TwitterUser.objects.get(user=self.twitter))
        response = self.client.post(reverse(oauthtwitter.associate),
                                    {'action': 'remove',
                                     'twitter_id': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertRaises(TwitterUser.DoesNotExist,
                          TwitterUser.objects.get, user=self.twitter)


    def test_callback(self):
        # User goes directly to the callback page.
        response = self.client.get(reverse(oauthtwitter.callback))
        self.assertEqual(response['Location'],
                         'http://testserver%s' % settings.LOGIN_URL)
        # User goes directly to the callback page. but tampers with oauth_token
        response = self.client.get(reverse(oauthtwitter.callback),
                                   {'oauth_token': 'bad'})
        self.assertEqual(response['Location'],
                         'http://testserver%s' % settings.LOGIN_URL)
        # User comes in through Twitter OAuth, but tampers with oauth_token
        o = self.mocker.patch(oauthtwitter)
        request = self.mocker.mock()
        request.GET
        self.mocker.result({'oauth_token': 'bad'})
        request.session
        self.mocker.result({})
        self.mocker.count(1, None)
        request.twitter_request_token
        self.mocker.result(TOKEN)
        # New user comes in through Twitter OAuth
        request.GET
        self.mocker.result({'oauth_token': 'a'})
        request.twitter_request_token
        self.mocker.result(TOKEN)
        Api = self.mocker.replace(TwitterApi)
        Api(TOKEN).getAccessToken()
        self.mocker.result(TOKEN)
        request.twitter_access_token = ANY
        request.user
        self.mocker.result(AnonymousUser())
        userinfo = self.mocker.mock()
        cui = self.mocker.replace(cached_user_info)
        cui(request, TOKEN)
        self.mocker.result(userinfo)
        o._authenticate(userinfo=userinfo)
        self.mocker.result(None)
        # Existing user comes in through Twitter OAuth
        request.GET
        self.mocker.result({'oauth_token': 'a'})
        request.twitter_request_token
        self.mocker.result(TOKEN)
        Api(TOKEN).getAccessToken()
        self.mocker.result(TOKEN)
        request.twitter_access_token = ANY
        request.user
        self.mocker.result(User.objects.get(username='password'))
        cui(request, TOKEN)
        self.mocker.result(userinfo)
        userinfo.id
        self.mocker.result(3)
        userinfo.AsJsonString()
        self.mocker.result('{}')
        with self.mocker:
            response = o.callback(request)
            self.assertEqual(response['Location'], settings.LOGIN_URL)
            response = o.callback(request)
            self.assertEqual(response['Location'],
                             reverse(oauthtwitter.register))
            response = o.callback(request)
            self.assertEqual(response['Location'],
                             '/twitter/associate/?associated=1')

    def test_signin(self):
        response = self.client.get(reverse(oauthtwitter.signin))
        prefix = 'http://twitter.com/oauth/authenticate?'
        self.assertTrue(response['Location'].startswith(prefix),
                        response['Location'])

    def test_register(self):
        # User goes directly to the register page.
        response = self.client.get(reverse(oauthtwitter.register))
        self.assertTrue(response['Location'], settings.LOGIN_URL)
        # User is logged in
        self.assertTrue(self.client.login(username='password',
                                          password='password'))
        response = self.client.get(reverse(oauthtwitter.register))
        self.assertTrue(response['Location'], '/home/')
        # New user comes in through Twitter
        request = self.mocker.mock()
        request.user
        self.mocker.result(AnonymousUser())
        self.mocker.count(1, None)
        RC = self.mocker.replace('django.template.RequestContext')
        RC(ANY)
        self.mocker.result({})
        request.twitter_access_token
        self.mocker.result(TOKEN)
        userinfo = self.mocker.mock()
        userinfo.screen_name
        self.mocker.result('unknown')
        request.twitter_userinfo
        self.mocker.result(userinfo)
        request.method
        self.mocker.result('GET')
        # New user posts form through Twitter
        request.twitter_access_token
        self.mocker.result(TOKEN)
        userinfo.id
        self.mocker.result(2)
        userinfo.screen_name
        self.mocker.result('unknown')
        userinfo.AsJsonString()
        self.mocker.result('{}')
        request.twitter_userinfo
        self.mocker.result(userinfo)
        request.method
        self.mocker.result('POST')
        request.POST
        self.mocker.result({'username': 'unknown'})
        o = self.mocker.patch(oauthtwitter)
        o._login_and_redirect(request=request, user=ANY)
        self.mocker.result('New user')
        with self.mocker:
            response = oauthtwitter.register(request)
            self.assertEqual(response.status_code, 200)
            response = o.register(request)
            self.assertEqual(response, 'New user')
            self.assertTrue(User.objects.get(username='unknown'))

    def test_authenticate(self):
        # Associated Twitter user
        twitter = self.mocker.mock()
        twitter.id
        self.mocker.result(1)
        # Unknown Twitter uesr
        unknown = self.mocker.mock()
        unknown.id
        self.mocker.result(2)
        with self.mocker:
            self.assertEqual(oauthtwitter._authenticate(twitter),
                             User.objects.get(username="twitter"))
            self.assertEqual(oauthtwitter._authenticate(unknown), None)

    def test_create_user(self):
        o = self.mocker.patch(oauthtwitter)
        request = self.mocker.mock()
        # User already logged in
        request.user.is_anonymous()
        self.mocker.result(False)
        o._login_and_redirect(request=request, user=None)
        self.mocker.result('Logged in')
        # Anonymous user with new User
        request.user.is_anonymous()
        self.mocker.result(True)
        request.twitter_access_token
        self.mocker.result(TOKEN)
        unknown = self.mocker.mock()
        unknown.id
        self.mocker.result(2)
        unknown.screen_name
        self.mocker.result("unknown")
        unknown.AsJsonString()
        self.mocker.result('{}')
        request.twitter_userinfo
        self.mocker.result(unknown)
        o._login_and_redirect(request=request,
                              user=MATCH(lambda x: isinstance(x, User)))
        self.mocker.result('New user')
        # Anonymous user with existing User
        request.user.is_anonymous()
        self.mocker.result(True)
        request.twitter_access_token
        self.mocker.result(TOKEN)
        twitter = self.mocker.mock()
        twitter.screen_name
        self.mocker.result("twitter")
        request.twitter_userinfo
        self.mocker.result(twitter)
        with self.mocker:
            response = o._create_user(request)
            self.assertEqual(response, 'Logged in')
            response = o._create_user(request)
            self.assertEqual(response, 'New user')
            response = o._create_user(request)
            self.assertEqual(response['Location'], '/twitter/register/')

    def test_login_and_redirect(self):
        o = self.mocker.patch(oauthtwitter)
        request = self.mocker.mock()
        # User already logged in
        twitter = User.objects.get(username='twitter')
        request.user
        self.mocker.result(twitter)
        # No User to log in
        True
        # Login a Twitter user
        o._login(request, twitter)
        request.user
        self.mocker.result(AnonymousUser())
        request.twitter_access_token
        self.mocker.result(TOKEN)
        userinfo = self.mocker.mock()
        userinfo.AsJsonString()
        self.mocker.result('{}')
        request.twitter_userinfo
        self.mocker.result(userinfo)
        with self.mocker:
            response = o._login_and_redirect(request, True)
            self.assertEqual(response['Location'], '/home/')
            response = o._login_and_redirect(request, None)
            self.assertEqual(response['Location'], '/home/')
            response = o._login_and_redirect(request, twitter)
            self.assertEqual(response['Location'], '/home/')
            self.assertEqual(str(twitter.twitter.access_token), str(TOKEN))
            self.assertEqual(twitter.twitter.userinfo_json, '{}')

    def test_on_new_user(self):
        # With auto_create_user
        request = self.mocker.mock()
        a = self.mocker.patch(OAuthTwitter(auto_create_user=True))
        a._create_user(request)
        self.mocker.result('auto_create')
        # Without
        b = self.mocker.patch(oauthtwitter)
        with self.mocker:
            response = a._on_new_user(request)
            self.assertEqual(response, 'auto_create')
            response = b._on_new_user(request)
            self.assertEqual(response['Location'], '/twitter/register/')

    def test_redirect_to_login(self):
        response = oauthtwitter._redirect_to_login(None)
        self.assertEqual(response['Location'], settings.LOGIN_URL)

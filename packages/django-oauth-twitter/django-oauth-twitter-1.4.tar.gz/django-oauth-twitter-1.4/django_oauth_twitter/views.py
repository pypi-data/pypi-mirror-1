from urllib2 import HTTPError

from django.conf import settings
from django.contrib.auth import login
from django.core.urlresolvers import get_callable, NoReverseMatch, reverse
from django.conf.urls.defaults import patterns, url
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from django_oauth_twitter.forms import RegistrationForm
from django_oauth_twitter.middleware import (cached_user_info,
                                             remove_tokens,
                                             set_access_token,
                                             set_request_token)
from django_oauth_twitter.models import (TwitterUser, TwitterAlreadyLinked,
                                         UserAlreadyLinked)
from django_oauth_twitter.utils import fail_whale, TwitterApi, update_qs

from oauth.oauth import OAuthToken


class OAuthTwitter(object):
    RegistrationForm=RegistrationForm

    def __init__(self,
                 auto_create_user=False,
                 association_url=None,
                 no_thanks_url='django.contrib.auth.views.logout',
                 registration_url=None,
                 signed_in_url='/'):
        self.auto_create_user = auto_create_user
        if association_url is None:
            self.association_url = LazyReverse(self.associate)
        else:
            self.association_url = LazyReverse(association_url)
        self.no_thanks_url = LazyReverse(no_thanks_url)
        if registration_url is None:
            self.registration_url = LazyReverse(self.register)
        else:
            self.registration_url = LazyReverse(registration_url)
        self.signed_in_url = LazyReverse(signed_in_url)

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^callback/', self.callback, name='twitter_callback'),
            url(r'^signin/', self.signin, name='twitter_signin'),
        )
        if self.association_url.location == self.associate:
            # Add ^associate/ location if we're meant to handle association.
            urlpatterns += patterns('',
                url(r'^associate/', self.association_url.location,
                    name='twitter_associate')
            )
        if self.registration_url.location == self.register:
            # Add ^register/ location if we're meant to handle registration.
            urlpatterns += patterns('',
                url(r'^register/', self.registration_url.location,
                    name='twitter_register')
            )
        return urlpatterns
    urls = property(get_urls)

    def associate(self, request,
                  template="django_oauth_twitter/associate.html",
                  dictionary=None,
                  post_associate=None,
                  post_remove=None):
        user = request.user
        try:
            if not user.is_authenticated():
                return self._redirect_to_login(request)
            if request.method == 'POST':
                if request.POST.get('action') == 'remove':
                    try:
                        twitter_id = int(request.POST.get('twitter_id'))
                    except ValueError:
                        twitter_id = None
                    try:
                        twitter_user = user.twitter
                        if twitter_user.twitter_id == twitter_id:
                            twitter_user.delete()
                        del user._twitter_cache
                        remove_tokens(request)
                        if post_remove is not None:
                            post_remove(request)
                    except TwitterUser.DoesNotExist:
                        pass
            else:
                try:
                    twitter_user = request.user.twitter
                except TwitterUser.DoesNotExist:
                    twitter_user = None
                if request.GET.get('associated') and twitter_user is not None:
                    if post_associate is not None:
                        post_associate(request)
                    return HttpResponseRedirect(request.path)
            if dictionary is None:
                dictionary = {}
            dictionary.update({'error': request.GET.get('error'),
                               'error_user': request.GET.get('user')})
            return render_to_response(template, dictionary=dictionary,
                                      context_instance=RequestContext(request))
        except Exception, e:
            raise


    def callback(self, request):
        """
        Gets the oauth_token from Twitter and signs in a User.

        Note: You must set this callback URL in Twitter's Application
        Details page.  Twitter ignores OAuth's oauth_callback option.
        """
        @fail_whale
        def access_token(request_token):
            try:
                return TwitterApi(request_token).getAccessToken()
            except HTTPError, e:
                if e.code == 401:
                    return HttpResponseRedirect(reverse(self.signin))
                raise
        # Ensure that the user came in through signin().
        request_token = request.twitter_request_token
        if request_token is None:
            return self._redirect_to_login(request=request)
        # Ensure that the session's token matches Twitter's token.
        if request_token.key != request.GET.get('oauth_token'):
            remove_tokens(request)
            return self._redirect_to_login(request=request)
        # Save the access token in the session.
        access_token = access_token(request_token)
        if isinstance(access_token, HttpResponse):
            return access_token
        set_access_token(request, access_token)
        userinfo = cached_user_info(request, access_token)
        user = request.user
        if user.is_anonymous():
            # Find the User by the access token.
            user = self._authenticate(userinfo=userinfo)
            if user is None:
                # New user
                return self._on_new_user(request=request)
            return self._login_and_redirect(request=request, user=user)
        else:
            try:
                TwitterUser.objects.create_twitter_user(
                    user=user,
                    access_token=access_token,
                    userinfo=userinfo
                )
            except UserAlreadyLinked:
                return HttpResponseRedirect(
                    update_qs(self.association_url,
                              {'error': 'user_already_linked',
                               'user': user.username})
                )
            except TwitterAlreadyLinked:
                return HttpResponseRedirect(
                    update_qs(self.association_url,
                              {'error': 'twitter_already_linked',
                               'user': userinfo.screen_name})
                )
            # Add ?associated=1 to self.association_url
            association_url = update_qs(self.association_url,
                                        {'associated': '1'})
            return HttpResponseRedirect(association_url)

    def signin(self, request):
        """Redirects a user to the Twitter authorization page."""
        @fail_whale
        def get_signin_url(request):
            twitter = TwitterApi()
            request_token = twitter.getRequestToken()
            set_request_token(request, request_token)
            return twitter.getSigninURL(request_token)
        return HttpResponseRedirect(get_signin_url(request))

    def register(self, request,
                 template='django_oauth_twitter/register.html',
                 dictionary=None):
        # Ensure that the user has an access token
        access_token = request.twitter_access_token
        if access_token is None:
            return self._redirect_to_login(request=request)
        if request.user.is_anonymous():
            userinfo = request.twitter_userinfo
            screen_name = userinfo.screen_name
            if request.method == "POST":
                # Register the user
                form = self.RegistrationForm(request.POST,
                                             access_token=access_token,
                                             userinfo=userinfo)
                if form.is_valid():
                    user = form.save()
                    return self._login_and_redirect(request=request,
                                                    user=user)
            else:
                # Pre-fill with the user's Twitter screen name
                form = self.RegistrationForm(initial={'username': screen_name})
            if dictionary is None:
                dictionary = {}
            dictionary.update({'form': form,
                               'no_thanks': self.no_thanks_url,
                               'screen_name': screen_name})
            return render_to_response(template, dictionary=dictionary,
                                      context_instance=RequestContext(request))
        return HttpResponseRedirect(self.signed_in_url)

    def _authenticate(self, userinfo):
        """
        Returns user if `userinfo` is associated with a known user.
        Otherwise, returns None.
        """
        if userinfo is None:
            return None
        try:
            user = TwitterUser.objects.get(twitter_id=userinfo.id).user
        except TwitterUser.DoesNotExist:
            return None
        return user

    def _create_user(self, request):
        """
        Creates a User from their Twitter account and redirects to `url`.

        Afterwards, `login_and_redirect` to `url`.
        """
        user = None
        if request.user.is_anonymous():
            # Create the User
            access_token = request.twitter_access_token
            userinfo = request.twitter_userinfo
            form = self.RegistrationForm({'username': userinfo.screen_name},
                                         access_token=access_token,
                                         userinfo=userinfo)
            if form.is_valid():
                user = form.save()
            else:
                return HttpResponseRedirect(self.registration_url)
        # Login and redirect
        return self._login_and_redirect(request=request, user=user)

    def _login(self, request, user):
        # Nasty but necessary - annotate user and pretend it was the regular
        # auth backend. This is needed so django.contrib.auth.get_user works:
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

    def _login_and_redirect(self, request, user):
        """
        Login `user` with `access_token` and redirects to `signed_in_url`.

        If the `request.user` is already logged in, don't clobber the
        login with `user`.  The `request.user` has to log out first.
        """
        if user is not None and request.user.is_anonymous():
            # Login
            self._login(request, user)
            # Update the access_token
            twitter = user.twitter
            save = False
            if twitter.update_access_token(request.twitter_access_token):
                save = True
            if twitter.update_userinfo(request.twitter_userinfo):
                save = True
            if save:
                twitter.save()
        # Redirect
        return HttpResponseRedirect(self.signed_in_url)

    def _on_new_user(self, request):
        """
        Handles an AnonymousUser who has just authenticated with Twitter.

        If `self.auto_create_user` is True, creates a new User with a
        username matching their Twitter screen name.  Otherwise,
        redirects the user into the registration process.
        """
        if self.auto_create_user:
            return self._create_user(request)
        return HttpResponseRedirect(self.registration_url)

    def _redirect_to_login(self, request):
        """Redirect to settings.LOGIN_URL."""
        return HttpResponseRedirect(settings.LOGIN_URL)


class LazyReverse(object):
    def __init__(self, location):
        self.location = location
        self.url = None

    def __str__(self):
        if callable(self.location) or '/' not in self.location:
            self.url = reverse(self.location)
        else:
            self.url = self.location
        return self.url

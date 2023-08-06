import django.dispatch


# This signal is sent after a TwitterUser is created.
twitter_user_created = django.dispatch.Signal(providing_args=['twitter_user'])

Skin Switcher
=============

Switches the skin to "Plone Default" when we are editing.  We are
editing when our url is something like http://edit.domain.org/


Testing
-------

We rely on the getURL() method.  So we check that we can fool the test
instance into believing it is on a different url::

    >>> from collective.editskinswitcher.tests.utils import TestRequest
    >>> TestRequest().getURL()
    'http://127.0.0.1'
    >>> TestRequest(SERVER_URL='http://edit.domain.org').getURL()
    'http://edit.domain.org'

For testing purposes we make a new default skin.  We want to entertain
the visitors of this site, so we make a Monty Python Skin.  We use a
helper function here as the details are not interesting.

    >>> from collective.editskinswitcher.tests.utils import new_default_skin
    >>> context = portal
    >>> context.getCurrentSkinName()
    'Plone Default'
    >>> new_default_skin(portal)
    >>> context.getCurrentSkinName()
    'Monty Python Skin'

On localhost we show visitors the normal skin::

    >>> context.switchskin(context, TestRequest(SERVER_URL='http://localhost'))
    >>> context.getCurrentSkinName()
    'Monty Python Skin'

We have smart content editors as they know they can go to 127.0.0.1
and view the same site.  They get a different skin then, which is the
whole purpose of this package.  Content editors should be happy with
just the Plone Default skin::

    >>> context.switchskin(context, TestRequest(SERVER_URL='http://127.0.0.1'))
    >>> context.getCurrentSkinName()
    'Plone Default'

In these tests we need to manually switch the skin back to our
default, which normally happens automatically when your browser makes
a new request.

    >>> context.changeSkin('Monty Python Skin')

Visitors on localhost still see our fabulous Monty Python Skin::

    >>> context.switchskin(context, TestRequest(SERVER_URL='http://localhost'))
    >>> context.getCurrentSkinName()
    'Monty Python Skin'

Any content editors that arrive via a url beginning with 'edit' (or
'cms' or 'manage') will get their beloved Plone Default skin again::

    >>> context.switchskin(context, TestRequest(SERVER_URL='http://edit.domain.org'))
    >>> context.getCurrentSkinName()
    'Plone Default'

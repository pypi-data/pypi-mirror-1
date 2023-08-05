Collective edit skin switcher
=============================

For a customer of `Zest Software`_ I [Maurits van Rees] created a
package called ``collective.editskinswitcher``.  I gladly took some code
from colleague Mark van Lent who did something similar for a different
web site.  The package is on the Cheese Shop so it can be easy
installed.  And the code is in the Plone collective_.

.. _`Zest Software`: http://zestsoftware.nl
.. _collective: http://svn.plone.org/svn/collective/collective.editskinswitcher/


What does it do?
----------------

Let's say you have a Plone Site.  I tested this with Plone 3.  I see
no reason why it should fail on Plone 2.5.  Maybe it even works on a
CMF site.  Anyway, whatever site you have is available on two urls:
``www.yourdomain.com`` and ``edit.yourdomain.com``.  Some day you
should ask your local Apache guru how he did that.

With ``collective.editskinswitcher`` installed (with the portal quick
installer), visitors that go to the website with the url
``edit.yourdomain.com`` will see the Editor Skin.  (This can be set in
a property, as we shall see later.)  Visitors to
``www.yourdomain.com`` will see whatever skin you have set as the
default skin in portal_skins.  Can be pretty handy.

To avoid confusion: we will call what you have set as "default skin"
the Visitor Skin.  And the skin meant for editors we call the Editor
Skin.

Developer types probably like the fact that you also get the Visitor
Skin when visiting ``localhost`` and the Editor Skin when you go to
``127.0.0.1``.

Other options
-------------

There are some options you can set.  Go to ``portal_properties``, and
then go to the ``editskin_switcher`` property sheet.  These options
are available:

- ``edit_skin``: set the skin that editors get.  The default is "Plone
  Default".

- ``based_on_url``: when True (the default) you get the behaviour
  described above.

- ``need_authentication``: when True you need to be logged in before
  your skin is switched.  By default this is set to False.  This looks
  for the ``__ac`` cookie that Plone gives you when logged in.  Note:
  logging in via the Zope Management Interface is handled without
  cookies, so the editskin switcher regards you as anonymous then.

You can combine the two behaviours if you want.  If they are both
True, then you need to have the right url and you need to be logged
in.

When both are False, nothing happens: then you might as well simply
uninstall this product as it is not useful.


Why not CMFUrlSkinSwitcher?
---------------------------

I looked at CMFUrlSkinSwitcher first but it had not been touched in
two years.  One import error (CMFCorePermissions) could easily be
fixed as that import was not even used.  But after that tests were
failing all over the place.  Theoretically always fixable of course,
but rolling an own package seemed easier, cleaner and faster.

Also, CMFUrlSkinSwitcher does some more things.  At least it messes
around with some methods like absolute_url.  It could be that I find
out later that this is necessary in ``collective.editskinswitcher`` too,
but currently it does not look like that will be the case.


How do I know this is working?
------------------------------

The easiest way to test this package in a default plone site (apart
from running the tests of course), is:

- Install ``collective.editskinswitcher``.

- Go to portal_skins in the ZMI.

- Create a new skin selection based on Plone Default.  Call this
  "Visitor Skin".

- Make Visitor Skin the default skin.

- Remove the custom skin layer from Plone Default.

- Customize the main template or the logo or something else that
  is easy to spot.

- Visit ``127.0.0.1:8080/plonesite`` and you will see default Plone.

- Visit ``localhost:8080/plonesite`` and you will see Plone with
  your customization.


On Linux you can edit ``/etc/hosts`` and add a line like::

  127.0.0.1 edit.yourdomain.com www.yourdomain.com

Now visiting ``edit.yourdomain.com`` should give you the Editor Skin
and ``www.yourdomain.com`` should give you the Visitor Skin with the
customizations.


You can also let the edit urls begin with ``cms`` or ``manage``.  As
long as the url is something like::

  ...//(edit|cms|manage).something.something....

you end up in the edit skin.


Have fun!

Maurits van Rees

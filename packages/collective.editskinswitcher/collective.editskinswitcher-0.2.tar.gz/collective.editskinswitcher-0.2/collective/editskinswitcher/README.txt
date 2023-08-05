Collective Edit Skin Switcher
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
``edit.yourdomain.com`` will see the Plone Default skin, which is
meant for content editors.  Visitors to ``www.yourdomain.com`` will
see whatever skin you have set as the default skin in portal_skins.
Can be pretty handy.

Developer types probably like the fact that you also get the default
skin when visiting ``localhost`` and the edit skin when you go to
``127.0.0.1``.

But maybe you want to turn it around: your visitors should see Plone
Default and your editors should see your brilliant Monty Python Skin!
Ni!  Just go to the ``portal_properties``, then ``editskin_switcher``
and change the ``edit_skin`` property to your dashing theme.


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

- Create a new skin selection based on Plone Default.  In the tests I
  call this Monty Python Skin, so I will use that term here as well.

- Make Monty Python Skin the default skin.

- Remove the custom skin layer from Plone Default.

- Customize the main template or the logo or something else that
  is easy to spot.

- Visit ``127.0.0.1:8080/plonesite`` and you will see default Plone.

- Visit ``localhost:8080/plonesite`` and you will see Plone with
  your customization.


On Linux you can edit ``/etc/hosts`` and add a line like::

  127.0.0.1 edit.yourdomain.com www.yourdomain.com

Now visiting ``edit.yourdomain.com`` should give you default Plone and
``www.yourdomain.com`` should give you the customized Plone.


You can also let the edit urls begin with ``cms`` or ``manage``.  As
long as the url is something like::

  ...//(edit|cms|manage).something.something....

you end up in the edit skin.


Have fun!

Maurits van Rees

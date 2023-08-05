from zope.publisher.browser import TestRequest
from Products.CMFCore.utils import getToolByName


def _hold(self, object):
    """Hold a reference to an object to delay it's destruction until mine

    Taken from ZPublisher/BaseRequest.py
    Needed by CMFCore/Skinnable.py(142)changeSkin()
    """
    if self._held is not None:
        self._held=self._held+(object, )

TestRequest._hold = _hold


def new_default_skin(portal):
    """Make new default skin based on Plone Default.
    """
    sk_tool = getToolByName(portal, 'portal_skins')
    skinpath = sk_tool.getSkinPath('Plone Default')
    sk_tool.addSkinSelection('Monty Python Skin', skinpath)
    sk_tool.default_skin = 'Monty Python Skin'

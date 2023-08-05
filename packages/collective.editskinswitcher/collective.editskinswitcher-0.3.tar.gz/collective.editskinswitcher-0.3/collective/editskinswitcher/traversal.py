from collective.editskinswitcher.utils import is_edit_url
from Products.CMFCore.utils import getToolByName


def switch_skin(object, event):
    """Switch the skin if needed
    """
    """Switch to the Plone Default skin when we are editing.
    """
    context = object
    request = event.request
    portal_props = getToolByName(context, 'portal_properties')
    if portal_props is None:
        return None
    editskin_props = portal_props.get('editskin_switcher')
    if editskin_props is None:
        return None
    # Okay, we have a property sheet we can use.
    edit_skin = editskin_props.getProperty('edit_skin', '')
    based_on_url = editskin_props.getProperty('based_on_url', True)
    need_authentication = editskin_props.getProperty('need_authentication',
                                                     False)
    if not based_on_url and not need_authentication:
        # This makes no sense.  Just uninstall this product and use
        # the default skin.
        return None
    if based_on_url and not is_edit_url(request.getURL()):
        return None
    # Note: we need to check for cookies as a call like to
    # portal_membership.isAnonymousUser() works fine in our tests, but
    # not in real life.  Probably because our switch_skin method is
    # used as an AccessRule.
    if need_authentication and not request.cookies.get('__ac'):
        return None
    # If the edit_skin does not exist, the next call is
    # intelligent enough to use the default skin instead.
    context.changeSkin(edit_skin, request)
    return None

from collective.editskinswitcher.utils import is_edit_url
from Products.CMFCore.utils import getToolByName


def switch_skin(context, REQUEST=None):
    """Switch to the Plone Default skin when we are editing.
    """
    url = REQUEST.getURL()
    if is_edit_url(url):
        edit_skin = ''
        portal_props = getToolByName(context, 'portal_properties')
        if portal_props is not None:
            editskin_props = portal_props.get('editskin_switcher')
            if editskin_props is not None:
                edit_skin = editskin_props.getProperty('edit_skin', '')
        # If edit_skin is an empty string or the skin does not exist,
        # the next call is intelligent enough to use the default skin
        # instead.
        context.changeSkin(edit_skin, REQUEST)
    return None

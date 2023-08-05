from collective.editskinswitcher.utils import is_edit_url


def switch_skin(context, REQUEST=None):
    """Switch to the Plone Default skin when we are editing.
    """
    url = REQUEST.getURL()
    if is_edit_url(url):
        context.changeSkin('Plone Default', REQUEST)
    return None

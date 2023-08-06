from zope import interface


class IExcludeFromSearch(interface.Interface):
    """ Do not show this content in searches.
    """
    pass
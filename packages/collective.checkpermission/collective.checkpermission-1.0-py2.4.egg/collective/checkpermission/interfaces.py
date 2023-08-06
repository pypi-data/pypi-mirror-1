from zope.interface import Interface


class ICheckPermission(Interface):
    """ 
    Check if permissions are ok.
    This is called from the check permission decorator. 
    """

    def check(permission):
        """ True if you have the rights to do something, otherwise raises Unauthorized """

from zope.interface import Interface

class IClioModel(Interface):
    """A model handled by Clio.
    """

class ICurrentUserId(Interface):
    def __call__():
        """Return the current user id.

        This is the user id of the current user (a unicode string).
        """


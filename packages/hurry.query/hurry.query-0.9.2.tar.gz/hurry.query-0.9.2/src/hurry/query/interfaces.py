from zope.interface import Interface

class IQuery(Interface):
    def searchResults(query):
        """Query indexes.

        Argument is a query composed of terms.
        """


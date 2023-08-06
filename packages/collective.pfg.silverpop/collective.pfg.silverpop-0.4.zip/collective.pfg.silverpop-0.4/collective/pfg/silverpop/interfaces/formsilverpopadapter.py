from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from collective.pfg.silverpop import silverpopMessageFactory as _


class IFormSilverpopAdapter(Interface):
    """A Form action adapter that will add a recipient to a
    Silverpop mailing list
    """

    def onSuccess(fields, REQUEST=None):
        """
        add recipient to silverpop
        """

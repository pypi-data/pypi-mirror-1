from zope.interface import Interface

class IWorkgroupActions(Interface):
    """ WorkgroupActions utility """
    def disable(context):
        """ Disable workgroup action """

    def enable(context):
        """ Enable workgroup action"""


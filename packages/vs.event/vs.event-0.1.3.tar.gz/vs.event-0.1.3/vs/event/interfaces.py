################################################################
# vs.event - published under the GPL 2
# Authors: Andreas Jung, Veit Schiele, Anne Wello
################################################################

from zope import interface

class IVSEvent(interface.Interface):
    """ marker interface for VSEvent """

class IVSSubEvent(IVSEvent):
    """ marker interface for VSSubEvent """

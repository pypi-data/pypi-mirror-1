
from zope.interface import implements
from zope.component import getMultiAdapter

from interfaces import IRuleOverwrite 

def beforeTraverseHandler(context, event):
    """ This handler is the main working horse and checks if
        public skin should be enabled. That means marking the
        request with IPublicSkinLayer. """

    skinner = getMultiAdapter( (context, event.request), name=u'skinner')
    if skinner.mustDisplayPublicView() is True:
        skinner.activatePublicSkin()

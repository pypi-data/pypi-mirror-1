"""Card notification hooks

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.selectors import implements
from cubicweb.sobjects.notification import ContentAddedView

class CardAddedView(ContentAddedView):
    """get notified from new cards"""
    __select__ = implements('Card')
    content_attr = 'synopsis'

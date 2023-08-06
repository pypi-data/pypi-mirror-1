"""cube-specific forms/views/actions/components

Specific views for cards

:organization: Logilab
:copyright: 2001-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import html_escape

from cubicweb.selectors import implements
from cubicweb.web import uicfg
from cubicweb.web.views import primary

uicfg.primaryview_section.tag_attribute(('Card', 'title'), 'hidden')
uicfg.primaryview_section.tag_attribute(('Card', 'synopsis'), 'hidden')
uicfg.primaryview_section.tag_attribute(('Card', 'wikiid'), 'hidden')

class CardPrimaryView(primary.PrimaryView):
    __select__ = implements('Card')
    show_attr_label = False

    def summary(self, entity):
        return entity.dc_description('text/html')


class CardInlinedView(CardPrimaryView):
    """hide card title and summary"""
    __regid__ = 'inlined'
    title = _('inlined view')
    main_related_section = False

    def render_entity_title(self, entity):
        pass

    def render_entity_metadata(self, entity):
        pass

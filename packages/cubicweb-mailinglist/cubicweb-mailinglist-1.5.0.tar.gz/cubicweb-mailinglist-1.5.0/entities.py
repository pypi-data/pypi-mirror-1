"""entity classes for mailing-list entities

:organization: Logilab
:copyright: 2003-2009 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.interfaces import ISiocContainer

class MailingList(AnyEntity):
    """customized class for MailingList entities"""
    __regid__ = 'MailingList'
    fetch_attrs, fetch_order = fetch_config(['name'])
    __implements__ = AnyEntity.__implements__ + (ISiocContainer,)

    # isioc interface
    def isioc_type(self):
        return 'MailingList'

    def isioc_items(self):
        return self.reverse_sent_on

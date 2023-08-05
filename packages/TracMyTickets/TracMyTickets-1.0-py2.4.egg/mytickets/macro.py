# Created by Noah Kantrowitz on 2007-07-29.
# Copyright (c) 2007 Noah Kantrowitz. All rights reserved.

from trac.core import *
from trac.wiki.api import IWikiMacroProvider
from trac.ticket.query import TicketQueryMacro

class MyTicketsMacro(TicketQueryMacro):
    """A simple macro to show your tickets."""

    implements(IWikiMacroProvider)

    def render_macro(self, req, name, content):
        content = (content or '').split(',')
        content[0] = (content[0] + '&owner=%s'%req.authname).lstrip('&')
        content = ','.join(content)
        return super(MyTicketsMacro, self).render_macro(req, name, content)


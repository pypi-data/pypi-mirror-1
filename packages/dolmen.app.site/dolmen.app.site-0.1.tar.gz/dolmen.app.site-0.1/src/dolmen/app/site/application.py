# -*- coding: utf-8 -*-

import grok
import dolmen.content as content
from zope.interface import Interface


class IDolmen(Interface):
    """This interface defines a Dolmen site root.
    """


class Dolmen(grok.Application, content.Container):
    """A Dolmen Site Manager.
    """
    grok.implements(IDolmen)
    content.nofactory()
    title = u"My Dolmen Site"

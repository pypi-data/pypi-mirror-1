from sqlobject import *

from turbogears.database import PackageHub

hub = PackageHub("wiki20")
__connection__ = hub

class Page(SQLObject):
    pagename = UnicodeCol(alternateID=True, length=30)
    data = UnicodeCol()

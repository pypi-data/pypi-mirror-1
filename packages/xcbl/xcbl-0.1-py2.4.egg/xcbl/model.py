from sqlobject import *

from turbogears.database import PackageHub

hub = PackageHub("xcbl")
__connection__ = hub

# class YourDataClass(SQLObject):
#     pass


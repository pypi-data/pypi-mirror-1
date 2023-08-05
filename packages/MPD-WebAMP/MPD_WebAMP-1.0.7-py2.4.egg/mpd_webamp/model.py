from turbogears.database import PackageHub
from sqlobject import *

hub = PackageHub("mpd_webamp")
__connection__ = hub

# class YourDataClass(SQLObject):
#     pass


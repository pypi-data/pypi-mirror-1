from turbogears.database import PackageHub
from sqlobject import *

hub = PackageHub('fosswallproxy')
__connection__ = hub

# class YourDataClass(SQLObject):
#     pass


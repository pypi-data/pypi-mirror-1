from sqlobject import *

from turbogears.database import PackageHub

hub = PackageHub("turbogears.config_admin")
__connection__ = hub

def create_models():
    hub.begin()
    ConfigOption.createTable(ifNotExists=True)
    hub.commit()
    hub.end()

class ConfigOption(SQLObject):
    class sqlmeta:
        table = "configuration"
    name = StringCol(length=255)
    panel = StringCol(length=255)
    value = BLOBCol(length=16*1024**2)
    


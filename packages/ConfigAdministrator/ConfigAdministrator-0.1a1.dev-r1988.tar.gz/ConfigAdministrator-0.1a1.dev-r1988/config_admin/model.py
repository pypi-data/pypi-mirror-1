from sqlobject import *
import cPickle as pickle

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
    name = UnicodeCol(length=255)
    panel = UnicodeCol(length=255)
    value = BLOBCol(length=16*1024**2)
    
    def _set_value(self, value):
        return self._SO_set_value(pickle.dumps(value).encode('base64'))
    
    def _get_value(self):
        return pickle.loads(self._SO_get_value().decode('base64'))


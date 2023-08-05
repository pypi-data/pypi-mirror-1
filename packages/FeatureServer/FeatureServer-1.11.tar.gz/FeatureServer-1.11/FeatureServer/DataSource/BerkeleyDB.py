__author__  = "MetaCarta"
__copyright__ = "Copyright (c) 2006-2007 MetaCarta"
__license__ = "Clear BSD" 
__version__ = "$Id: BerkeleyDB.py 396 2007-12-31 07:24:33Z crschmidt $"

from FeatureServer.DBM import DBM
from FeatureServer.DataSource import DataSource
import bsddb
import _bsddb

class BerkeleyDB (DBM):
    """BerkleyDB is a specialized form of DBM, using the bsddb
       module. This is known not to work on OS X, as the bsddb
       module does not work."""
    def __init__(self, name, writable = 0, lockfile = None, **args):
        DataSource.__init__(self, name, **args)
        self.db = bsddb.rnopen( args["file"] )
        self.append = self.db.db.append
        self.writable = int(writable)
        if self.writable and lockfile:
            self.lock = Lock(lockfile)
        else:
            self.lock = None

    def __iter__ (self):
        self.startIteration = True
        return self
        
    def next (self):
        if self.startIteration:
            self.startIteration = False
            return self.db.last()[0]
        try:
            return self.db.previous()[0]
        except _bsddb.DBNotFoundError:
            raise StopIteration    

from sqlobject import *
from turbogears.database import AutoConnectHub
from sqlobject.mysql.mysqlconnection import MySQLConnection
import time
import threading
import MySQLdb

threadlocker = threading.Lock()
hub     = AutoConnectHub()

def connect(threadIndex):
    """ Function to create a connection at the start of the thread """
    hub.threadConnection = MySQLConnection('spiderpydb','root','sniggle','localhost',3306) #AutoConnectHub()#
class RootSite(SQLObject):
    _connection = hub
    address = StringCol()
    user = ForeignKey('User')
class Word(SQLObject):
    _connection = hub
    data = StringCol()
    entries = MultipleJoin('Entry')
class Entry(SQLObject):
    _connection = hub
    #word = ForeignKey('Word')
    word = StringCol()
    uri = ForeignKey('URI')
    user = ForeignKey('User') 
class URI(SQLObject):
    _connection = hub
    address = StringCol()
    data = StringCol()
    time = StringCol()
class Admin(SQLObject):
    _connection = hub
    #interval = IntCol()
    password = StringCol()
    email = StringCol()
class User(SQLObject):
    _connection = hub
    name = StringCol()
    password = StringCol()
    email = StringCol()
    wait = StringCol()
    rootSites = MultipleJoin('RootSite')
    que = MultipleJoin('Que')
class Que(SQLObject):
    _connection = hub
    #could be URI
    address = StringCol()
    time = FloatCol()
    user = ForeignKey('User')
def synch(func,*args):
   def wrapper(*args): 
      try: 
        threadlocker.acquire()
        return func(*args)
      finally:
        threadlocker.release()
   return wrapper
class ConnectionPool:
  def __init__(self, timeout=1, checkintervall=1):
    self.timeout=timeout
    self.lastaccess={}
    self.connections={}
    self.checkintervall=checkintervall
    self.lastchecked=time.time()
    self.lockingthread=None
  def getConnection(self):
    global hub
    tid=threading._get_ident()
    try:
      con=self.connections[tid]
    except KeyError:
      hub.threadConnection = MySQLConnection('spiderpydb','root','sniggle','localhost',3306)
      con = hub.threadConnection
      print 'key error re-connecting'
      self.connections[tid]=con
    self.lastaccess[tid]=time.time()
    if self.lastchecked + self.checkintervall < time.time():
      self.cleanUp()
    return con

  def getLock(self):
    while not self._checklock():	 
      #print 'in check lock'
      time.sleep(0.02)
    self.lockingthread=threading._get_ident()
  getLock=synch(getLock)  

  def relLock(self):
    self.lockingthread=None

  def _checklock(self):
    if self.lockingthread == threading._get_ident() or self.lockingthread is None:
      return True
    return False

  def cleanUp(self):
    dellist=[]
    for con in self.connections:
      if self.lastaccess[con] + self.timeout < time.time():
        self.connections[con].close()
        del self.lastaccess[con]
        dellist.append(con)
    for l in dellist:
      del self.connections[l]
      print 'deleted connections'
conpool = ConnectionPool()

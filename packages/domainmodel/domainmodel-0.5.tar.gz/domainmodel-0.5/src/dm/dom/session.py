from dm.dom.stateful import *
from dm.ioc import *
import md5
import random
import sys
import mx.DateTime
from dm.dictionarywords import WEBKIT_NAME
from dm.dictionarywords import DJANGO_SECRET_KEY
from dm.dictionarywords import PYLONS_SECRET_KEY
from dm.exceptions import WebkitError

class Session(SimpleDatedObject):
    "Visitor session."

    registerKeyName = 'key'
    isUnique        = False
    key             = String(default='', isRequired=False)
    person          = HasA('Person', default=None)
    lastVisited     = DateTime(default=mx.DateTime.now)

    def initialise(self, register):
        super(Session, self).initialise(register)
        if not self.key:
            self.key = self.createKey()
            self.isChanged = True

    def createKey(self):
        "Returns new session key."
        webkitName = self.dictionary[WEBKIT_NAME]
        if webkitName == 'django':
            secretKey = self.dictionary[DJANGO_SECRET_KEY] 
        elif webkitName == 'pylons':
            secretKey = self.dictionary[PYLONS_SECRET_KEY] 
        else:
            secretKey = 'soso' 
        randomStr = str(random.randint(0, sys.maxint - 1)) + secretKey
        return md5.new(randomStr).hexdigest()

    def updateLastVisited(self):
        self.lastVisited = mx.DateTime.now()
        self.save()
        

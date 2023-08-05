from dm.dom.stateful import *
from dm.ioc import *
import md5
import random
import sys
import mx.DateTime

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
        secretKey = self.dictionary['django.secret_key'] 
        randomStr = str(random.randint(0, sys.maxint - 1)) + secretKey
        return md5.new(randomStr).hexdigest()

    def updateLastVisited(self):
        self.lastVisited = mx.DateTime.now()
        self.save()
        

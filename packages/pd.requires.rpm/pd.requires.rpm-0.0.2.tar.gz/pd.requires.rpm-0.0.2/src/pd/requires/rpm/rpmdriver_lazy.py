### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to presient rpm database as features set 

$Id: rpmdriver_lazy.py 51084 2008-05-10 12:53:31Z cray $
"""
__author__  = "Andrey Orlov, 20008"
__license__ = "GPL"
__version__ = "$Revision: 51084 $"

def _(s) : return s

import sys, os
from pd.lib.lazy import Lazy



class SimpleRPMStorageDriver(object) :
    name = u"This is RPM storage driver"

    def __init__(self) :
        self.cache = {}
        
    @Lazy
    def items(self) :
        return [ (item, SimpleRPMFeaturesDriver(self, qrpm=item)) for item in self.keys() ]
            
    @Lazy
    def normalize(self,item) :
        return os.popen("rpm -q '%s'" % item).read().strip()

    def __getitem__(self,item) :
        return self.__getitem__2(self.normalize(item))

    @Lazy
    def __getitem__2(self,item) :
        return SimpleRPMFeaturesDriver(self, qrpm=item)            

    @Lazy
    def keys(self) :
        return [ item.strip() for item in os.popen('rpm -qa').xreadlines() ]

    @Lazy
    def values(self) :
        return [ self.__getitem__2(item) for item in self.keys() ]

    @Lazy
    def getItemByFeature(self,feature) :
        return [ (item.strip(), self.__getitem__2(item.strip())) for item in os.popen("rpm -q --whatprovides '%s'" % feature).xreadlines() ]
            
    @Lazy            
    def getItemByRequires(self,feature) :
        return [ (item.strip(), self.__getitem__2(item.strip())) for item in os.popen("rpm -q --whatrequires '%s'" % feature).xreadlines() ]

        

class SimpleRPMFeaturesDriver(object) :
    def __init__(self,driver,rpm=None,qrpm = None) :
        self.driver = driver
        if qrpm is not None :
            self.__name__ = qrpm
        elif rpm is not None :
            self.__name__ = os.popen("rpm -q '%s'" % rpm).read().strip()
        else :
            raise TypeError,"Argument required"            
        
    def __repr__(self) :
        return "<%s.%s object of %s at %s>" % (self.__class__.__module__,self.__class__.__name__,self.__name__,hex(id(self)))

    def __str__(self) :
        return self.__name__        

    @Lazy
    def provides(self) :
        return set([x.strip().split(" ")[0] for x in os.popen("rpm -q --provides %s" % self.__name__).readlines()])
 
    @Lazy
    def requires(self) :
        return set([x.strip().split(" ")[0] for x in os.popen("rpm -q --requires %s" % self.__name__).readlines()])
 

    
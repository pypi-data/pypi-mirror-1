### -*- coding: utf-8 -*- #############################################
#######################################################################
"""This module developed to presient rpm database as features set 

$Id: rpmdriver.py 51060 2008-05-04 15:13:51Z cray $
"""
__author__  = "Andrey Orlov, 20008"
__license__ = "GPL"
__version__ = "$Revision: 51060 $"

def _(s) : return s

import sys, os


class SimpleRPMStorageDriver(object) :
    name = u"This is RPM storage driver"

    def items(self) :
        for item in self.keys() :
            yield item, SimpleRPMFeaturesDriver(qrpm=item)
            
    def __getitem__(self,item) :
        return SimpleRPMFeaturesDriver(item)            

    def keys(self) :
        for item in os.popen('rpm -qa').xreadlines() :
            yield item.strip()

    def values(self) :
        for item in self.keys() :
            yield SimpleRPMFeaturesDriver(qrpm=item)

    def getItemByFeature(self,feature) :
        for item in os.popen("rpm -q --whatprovides '%s'" % feature).xreadlines() :
            yield (item.strip(), SimpleRPMFeaturesDriver(qrpm=item.strip()))
            
    def getItemByRequires(self,feature) :
        for item in os.popen("rpm -q --whatrequires '%s'" % feature).xreadlines() :
            yield item.strip(), SimpleRPMFeaturesDriver(qrpm=item.strip())


class SimpleRPMFeaturesDriver(object) :
    def __init__(self,rpm=None,qrpm = None) :
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
        
    @property
    def provides(self) :
        return set([x.strip().split(" ")[0] for x in os.popen("rpm -q --provides %s" % self.__name__).readlines()])
 
    @property
    def requires(self) :
        return set([x.strip().split(" ")[0] for x in os.popen("rpm -q --requires %s" % self.__name__).readlines()])
 


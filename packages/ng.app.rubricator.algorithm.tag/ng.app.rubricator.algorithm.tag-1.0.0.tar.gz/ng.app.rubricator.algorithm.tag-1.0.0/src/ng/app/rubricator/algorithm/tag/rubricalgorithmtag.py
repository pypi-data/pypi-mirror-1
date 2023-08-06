### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The rubricalgorithm base class.

$Id: rubricalgorithmtag.py 51595 2008-08-31 22:04:07Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51595 $"

from zope.interface import implements
from zope.app.zapi import getUtilitiesFor
from interfaces import IRubricAlgorithmTag
from ng.app.rubricator.algorithm.base.rubricalgorithmbase import RubricAlgorithmBase
from ng.app.rubricator.tag.tagitemannotation.interfaces import ITagItemAnnotation
from zope.app.catalog.interfaces import ICatalog

class RubricAlgorithmTag(RubricAlgorithmBase):
    """Tag-based rubricator algorithm class """

    implements(IRubricAlgorithmTag)
    
    def rubricate(self, id, ob) :
        for name, utility in getUtilitiesFor(ICatalog) :
            print "rubricate ------->", id, ob
            for rubric in utility.searchResults(tags = {'any_of' : ITagItemAnnotation(ob).tags}) :
                self.link(id,ob,rubric)            

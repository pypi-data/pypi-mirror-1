### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based rubricalgorithm package

$Id: interfaces.py 51595 2008-08-31 22:04:07Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51595 $"

from zope.interface import Interface
from zope.schema import Field
from zope.app.container.interfaces import IContained
from zope.app.component.interfaces import ILocalSiteManager, ISiteManagementFolder
from zope.app.container.constraints import ContainerTypesConstraint

from ng.app.rubricator.algorithm.base.interfaces import IRubricAlgorithmDo, IRubricAlgorithmContained

class IRubricAlgorithmTagParam(Interface) :
    """ Parameters for tag-based rubrication algorithm """

class IRubricAlgorithmTag(IRubricAlgorithmDo, IRubricAlgorithmTagParam, IRubricAlgorithmContained ) :
    """ Content interface for tag-based rubric algorithm """

    
### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 52131 2008-12-23 08:53:16Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 51242 $"
 
from zope.interface import Interface
from ng.utility.interfacewave.interfaces import IPropagateInterface
from ng.app.rubricator.tag.tagrubricannotation.interfaces import ITagRubricAnnotationAble
                            
class ITagRubricAnnotationAblePropagate(ITagRubricAnnotationAble,IPropagateInterface) :
    """ Interface for rubric annotable by tag """
    

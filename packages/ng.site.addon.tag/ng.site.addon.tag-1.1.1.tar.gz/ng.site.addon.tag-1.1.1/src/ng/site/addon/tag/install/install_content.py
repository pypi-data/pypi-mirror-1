### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installRubricator script for the Zope 3 based ng.site.content.install
package

$Id: install_content.py 52164 2008-12-24 09:43:12Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52164 $"

from ng.site.addon.tag.wave.interfaces import ITagRubricAnnotationAblePropagate
from zope.interface import alsoProvides
def install_RubricInterface(context, **kw) :
    alsoProvides(context[u'rubricator'], ITagRubricAnnotationAblePropagate)
    return "Success"


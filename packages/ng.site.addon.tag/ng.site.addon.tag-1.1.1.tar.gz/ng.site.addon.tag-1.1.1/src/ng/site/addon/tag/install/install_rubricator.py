### -*- coding: utf-8 -*- #############################################
#######################################################################
"""installRubricator script for the Zope 3 based ng.site.content.install
package

$Id: install_rubricator.py 52157 2008-12-23 21:25:49Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52157 $"

from zope.app.component.site import SiteManagementFolder
from ng.app.rubricator.algorithm.tag.rubricalgorithmtag import RubricAlgorithmTag 
from ng.app.rubricator.algorithm.tag.interfaces import IRubricAlgorithmTag 

def install_RubricAlgoritmTag(context, **kw) :
    
    sm = context.getSiteManager()
    rubricator = sm[u'rubricator'] 
    rat = rubricator[u'RubricAlgorithmTag'] = RubricAlgorithmTag()
    
    sm.registerUtility(rat, provided=IRubricAlgorithmTag)

    return "Success"


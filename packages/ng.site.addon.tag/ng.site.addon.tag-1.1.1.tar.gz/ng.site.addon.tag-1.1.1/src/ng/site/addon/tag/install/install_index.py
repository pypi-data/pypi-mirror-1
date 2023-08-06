### -*- coding: utf-8 -*- #############################################
#######################################################################
"""The install_index script for the Zope 3 based ng.site.addon.tag.install package

$Id: install_index.py 52158 2008-12-24 09:10:27Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52158 $"

from zc.catalog.catalogindex import SetIndex

from ng.app.rubricator.tag.tagrubricannotation.interfaces import ITagRubricSearch
from zc.catalog.interfaces import IIndexValues 

def install_Index(context, **kw):
    """ Install Indexes """
    
    sm = context.getSiteManager()
    catalog = sm['Catalog'] 
    catalog['tags'] = SetIndex(field_name=u'tags',interface=ITagRubricSearch, field_callable=False)
    sm.registerUtility(catalog['tags'],provided=IIndexValues,name='tags')  

    return "Success"

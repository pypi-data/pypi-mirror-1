### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Project adapter  for the Zope 3 based projectannotation package

$Id: projectannotationableadapter.py 52311 2009-01-12 21:37:10Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52311 $"

from projectannotation import ProjectAnnotation
from zope.annotation.interfaces import IAnnotations 
from zope.schema import getFieldNames
from zope.location.location import LocationProxy 
from interfaces import projectannotationkey
from zope.security.proxy import removeSecurityProxy

def IProjectAnnotationAbleAdapter(context) :
    try :
        an = LocationProxy(
            removeSecurityProxy(IAnnotations(context)[projectannotationkey]),
                context,
                "++annotations++" + projectannotationkey
		)
    except KeyError :
    	dsa = IAnnotations(context)[projectannotationkey] = ProjectAnnotation()
        an = LocationProxy( removeSecurityProxy(dsa), context, "++annotations++" + projectannotationkey )

    return an

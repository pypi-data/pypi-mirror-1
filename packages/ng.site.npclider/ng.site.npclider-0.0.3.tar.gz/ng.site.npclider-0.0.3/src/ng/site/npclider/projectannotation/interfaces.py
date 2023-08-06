### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based product package

$Id: interfaces.py 52311 2009-01-12 21:37:10Z cray $
"""
__author__  = "Andrey Orlov, 2008"
__license__ = "GPL"
__version__ = "$Revision: 52311 $"
 
from zope.interface import Interface
from zope.schema import Bool
from ng.content.annotation.annotationswitcher.interfaces import IAnnotationSwitcher

class IProjectAnnotationAble(Interface) :
    pass


class IProjectAnnotation(Interface) :
    isready = Bool(
        title=u"Ready",
        default=False,
        description=u"If project ready then flag is set",
    )

projectannotationkey="ng.site.ncplider.projectannotation.projectannotation.ProjectAnnotation"


class IAnnotationSwitcherProject(IAnnotationSwitcher,IProjectAnnotationAble) :
    """Project of NPCLider"""
    
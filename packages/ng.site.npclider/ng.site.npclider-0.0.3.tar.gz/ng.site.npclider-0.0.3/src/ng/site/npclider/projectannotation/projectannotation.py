### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Project class for the Zope 3 based product package

$Id: projectannotation.py 52311 2009-01-12 21:37:10Z cray $
"""
__author__  = "Andrey Orlov, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52311 $"

from persistent import Persistent
from zope.interface import implements
from interfaces import IProjectAnnotationAble, IProjectAnnotation

class ProjectAnnotation(Persistent) :
    __doc__ = IProjectAnnotation.__doc__
    implements(IProjectAnnotation)
    __parent__ = None

    isready = False

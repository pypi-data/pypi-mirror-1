"""
$Id: viewlet.py 1965 2007-05-22 03:41:22Z hazmat $
"""

from zope.app.annotation.interfaces import IAnnotations
from zope.interface import implements

from zope import schema
from persistent.dict import PersistentDict
from zope.schema.interfaces import IContextSourceBinder, IIterableSource
from zope.schema.vocabulary import SimpleVocabulary

from Products.Five.formlib.formbase import FormBase, SubPageForm
from Products.CMFCore.utils import getToolByName

from interfaces import IViewComponent

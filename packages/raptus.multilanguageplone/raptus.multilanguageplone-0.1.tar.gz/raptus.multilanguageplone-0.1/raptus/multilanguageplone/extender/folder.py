from zope.component import adapts
from Products.ATContentTypes.content.folder import ATFolder

from base import DefaultExtender

class FolderExtender(DefaultExtender):
    adapts(ATFolder)
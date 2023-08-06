"""Definition of the ATFolderishDocument content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixinSchema

from collective.folderishpage import folderishpageMessageFactory as _
from collective.folderishpage.interfaces import IATFolderishDocument
from collective.folderishpage.config import PROJECTNAME

ATFolderishDocumentSchema = document.ATDocumentSchema + ConstrainTypesMixinSchema + schemata.NextPreviousAwareSchema + atapi.Schema((

))

schemata.finalizeATCTSchema(ATFolderishDocumentSchema, folderish=True, moveDiscussion=False)

class ATFolderishDocument(folder.ATFolder, document.ATDocument):
    """A page in the site. Can contain rich text."""
    implements(IATFolderishDocument)

    portal_type = "FolderishDocument"
    archetype_name = "Page"
    schema = ATFolderishDocumentSchema

atapi.registerType(ATFolderishDocument, PROJECTNAME)

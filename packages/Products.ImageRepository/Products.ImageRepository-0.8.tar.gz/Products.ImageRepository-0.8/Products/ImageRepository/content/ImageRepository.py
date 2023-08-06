from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import registerType
from Products.ImageRepository.interfaces import IImageRepository
from Products.ImageRepository.config import PROJECTNAME
from Products.ImageRepository import ImageRepositoryMessageFactory as _

from Products.ATContentTypes.atct import ATBTreeFolderSchema
from Products.ATContentTypes.atct import ATCTBTreeFolder
from Products.ATContentTypes.interfaces import IATBTreeFolder

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal

from Products.CMFPlone.interfaces.Translatable import ITranslatable

from Products.statusmessages.interfaces import IStatusMessage


def flatten(ltypes=(list, tuple), *args):
    for arg in args:
        if isinstance(arg, ltypes):
            for i in arg:
                for l in flatten(i):
                    yield l
        else:
            yield arg

def updateInterfaces(*args):
    return tuple(x for x in flatten(args) if x is not ITranslatable)


ImageRepositorySchema = ATBTreeFolderSchema.copy()

class ImageRepository(ATCTBTreeFolder):
    """A repository to store images."""
    implements(IImageRepository)

    content_icon   = 'imagerepository_icon.gif'
    meta_type      = 'ImageRepository'
    archetype_name = 'Image Repository'
    immediate_view = 'imagerepository_view'
    default_view   = 'imagerepository_view'
    suppl_views    = ()
    typeDescription= __doc__
    assocMimetypes = ()
    assocFileExt   = ()
    cmf_edit_kws   = ()

    schema = ImageRepositorySchema

    security = ClassSecurityInfo()

    __implements__ = updateInterfaces(ATCTBTreeFolder.__implements__, IATBTreeFolder)

    security.declarePrivate('at_post_create_script')
    def at_post_create_script(self):
        self.registerInKupu()

    security.declareProtected(ManagePortal, 'registerInKupu')
    def registerInKupu(self):
        """Registeres this repository as a library in Kupu."""
        request = self.REQUEST
        response = request.RESPONSE
        kupuTool = getToolByName(self, 'kupu_library_tool', None)
        if kupuTool is not None:
            portal_url = getToolByName(self, 'portal_url')
            library_ids = [x['id'] for x in kupuTool._libraries]
            repository_path = self.getPhysicalPath()
            portal = portal_url.getPortalObject()
            portal_path = portal.getPhysicalPath()
            sub_path = repository_path[len(portal_path):]
            path = "/".join(sub_path)
            name = "-".join(sub_path)
            if name not in library_ids:
                kupuTool.addLibrary(name,
                                    'string:%s' % self.pretty_title_or_id(),
                                    'string:${portal_url}/%s/imagerepository_collection.xml' % path,
                                    'string:${portal_url}/%s/imagerepository_collection.xml' % path,
                                    'string:${portal_url}/imagerepository_icon.gif')
                message = _(u"Registered repository in Kupu.")
        else:
            message = _("Kupu is not installed.")
        IStatusMessage(request).addStatusMessage(message, type='info')
        response.redirect(self.absolute_url()+'/view')

registerType(ImageRepository, PROJECTNAME)

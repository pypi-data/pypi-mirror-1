from zope import interface
from zope import component
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup import interfaces as gsinterfaces
from Products.CacheSetup import interfaces
from Products.CacheSetup.exportimport import atcontent

_PROJECT = 'CacheFu'
_FILENAME = 'cachesettings.xml'

def importSetup(context):
    """ Import setup.
    """
    site = context.getSite()
    logger = context.getLogger(_PROJECT)
    
    body = context.readDataFile(_FILENAME)
    if body is None:
        logger.info('Nothing to import.')
        return

    repo_tool = getToolByName(site, 'portal_cache_settings', None)
    if repo_tool is None:
        logger.info('Can not import without cache tool')
        return

    importer = component.queryMultiAdapter((repo_tool, context), gsinterfaces.IBody)
    if importer is None:
        logger.warning('Import adapter misssing.')
        return

    importer.body = body
    logger.info('setup imported.')

def exportSetup(context):
    """ Export setup.
    """
    site = context.getSite()
    logger = context.getLogger(_PROJECT)
    
    repo_tool = getToolByName(site, 'portal_cache_settings', None)
    if repo_tool is None:
        logger.info('Nothing to export.')
        return

    exporter = component.queryMultiAdapter((repo_tool, context), gsinterfaces.IBody)
    if exporter is None:
        return '%s: Export adapter misssing.' % _PROJECT

    context.writeDataFile(_FILENAME, exporter.body, exporter.mime_type)
    logger.info('setup exported.')


class CacheSettingsAdapter(atcontent.ATContentAdapterBase):
    _LOGGER_ID = "CacheSetup"
    name = "cachesettings"

    _fields = ['enabled', 'activePolicyId', 'proxyPurgeConfig', 'domains',
               'squidURLs', 'gzip', 'varyHeader']
    _pagecachemanager_fields = ["threshold",
                                "cleanup_interval",
                                "max_age",
                                "active"]

    def _exportNode(self):
        node = super(CacheSettingsAdapter, self)._exportNode()
        node.appendChild(self._extractPageCacheManager())
        return node


    def _extractPageCacheManager(self):
        fragment = self._doc.createDocumentFragment()
        mgr = getToolByName(self.context, "CacheSetup_PageCache", None)
        if mgr is None:
            return fragment

        node = self._doc.createElement("pagecachemanager")
        settings = mgr.getSettings()
        for fieldname in ["threshold", "cleanup_interval", "max_age", "active"]:
            prop = self._doc.createElement("property")
            prop.setAttribute("name", fieldname)
            value = self._convertValueToString(settings[fieldname])
            child = self._doc.createTextNode(value)
            prop.appendChild(child)
            node.appendChild(prop)

        fragment.appendChild(node)
        return fragment


    def _initPageCacheManager(self, node):
        mgr = getToolByName(self.context, "CacheSetup_PageCache", None)
        if mgr is None:
            return

        for child in node.childNodes:
            if child.nodeName != "pagecachemanager":
                continue

            newsettings = mgr.getSettings()
            for prop in child.childNodes:
                if prop.nodeName != "property":
                    continue

                name = str(prop.getAttribute("name"))
                value = self._getNodeText(prop)

                if isinstance(mgr._settings[name], int):
                    newsettings[name] = int(value)
                else:
                    newsettings[name] = value

                mgr.manage_editProps(mgr.Title(), newsettings)


    def _importNode(self, node):
        super(CacheSettingsAdapter, self)._importNode(node)
        self._initPageCacheManager(node)


class CachePolicyAdapter(atcontent.ATContentAdapterBase):
    _fields = ["title"]


class HeaderSetFolderAdapter(atcontent.ATContentAdapterBase):
    _fields = []


class HeaderSetAdapter(atcontent.ATContentAdapterBase):
    _fields = ['title', 'description', 'pageCache', 'lastModified',
               'etag', 'enable304s', 'vary', 'maxAge', 'sMaxAge', 
               'mustRevalidate', 'proxyRevalidate', 'noCache', 'noStore',
               'public', 'private', 'noTransform', 'preCheck', 
               'postCheck' ]


class RuleFolderAdapter(atcontent.ATContentAdapterBase):
    _fields = []




header_set_fields = ['varyExpression', 'lastModifiedExpression', 
                    'headerSetIdExpression', 'headerSetIdAuth', 
                    'headerSetIdAnon', 'predicateExpression', 'cacheStop']
etag_fields = ['etagExpression', 'etagTimeout', 'etagRequestValues', 
               'etagComponents']


class PolicyCacheRuleAdapter(atcontent.ATContentAdapterBase):
    _fields = ['title', 'description', 'cacheManager', 'types', 'ids',
               'cacheStop'] + header_set_fields

class ContentCacheRuleAdapter(atcontent.ATContentAdapterBase):
    _fields = ['title', 'description', 'contentTypes', 'defaultView',
               'templates', 'purgeExpression'] + \
              header_set_fields + etag_fields


class TemplateCacheRuleAdapter(atcontent.ATContentAdapterBase):
    _fields = ['title', 'description', 'templates'] + \
              header_set_fields + etag_fields

@component.adapter(interfaces.ICacheTool)
@interface.implementer(gsinterfaces.IFilesystemExporter)
def nullFilesystemExporter(object):
    pass

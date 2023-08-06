from collective.rooter import getNavigationRoot
from Products.CMFPlone.CatalogTool import CatalogTool

# Make portal_catalog's search function use a navigation root if no path parameter is given

CatalogTool._oldSearchResults = CatalogTool.searchResults

def searchResults(self, REQUEST=None, **kw):
    if 'path' not in kw and (REQUEST is None or 'path' not in REQUEST):
        root = getNavigationRoot()
        if root is not None:
            kw = kw.copy()
            kw['path'] = '/'.join(root.getPhysicalPath())
    return CatalogTool._oldSearchResults(self, REQUEST, **kw)

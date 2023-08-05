from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SkinInspector(BrowserView):

    template = ViewPageTemplateFile('skins.pt')

    def getSkinObjects(self, folder):
        object_ids = folder.objectIds()
        results = {
        }
        for oid in object_ids:
            obj = getattr(folder, oid)
            results[oid] = data = {}
            data['name'] = oid
            data['meta_type'] = obj.meta_type
            data['icon'] = obj.icon
            if obj.isPrincipiaFolderish:
                data['subobjects'] = self.getSkinObjects(obj)
        return results

    def __call__(self):
        skin_tool = getToolByName(self.context, 'portal_skins')
        self.dirs = self.getSkinObjects(skin_tool)
        self.skinpaths = skin_tool.getSkinPaths()
        results = []
        for skin, paths in self.skinpaths:
            path_info = []
            for path in paths.split(','):
                obj = self.dirs
                for name in path.split('/'):
                    obj = obj.get(name)
                    if obj is None:
                        break
                    obj = obj['subobjects']
                data = {
                    'name': path,
                }
                if obj is not None:
                    data['content'] = obj
                path_info.append(data)
            results.append({
                'name': skin,
                'paths': tuple(path_info),
            })
        self.skininfo = tuple(results)
        return self.template()

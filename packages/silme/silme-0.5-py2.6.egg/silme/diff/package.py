from silme.core.object import Blob, L10nObject, Comment, L10nPackage

def intersect(a, b):
    return list(set(a) & set(b))

class L10nPackageDiff:
    def __init__(self):
        self.packages = {}
        self.objects = {}
        self.id = None
        self.uri = None

    def empty(self):
        return not bool(len(self.packages)+len(self.objects))

    def add_package(self, l10npack_diff, path=None, type='modified'):
        if path == None or path=='':
            self.packages[l10npack_diff.id] = {'package':l10npack_diff, 'type': type}
        else:
            path = path.split('/')
            if path[0] in self.packages:
                self.packages[path[0]].add_package(l10npack_diff, '/'.join(path[1:]), type)
            else:
                sub_l10npack_diff = L10nPackageDiff()
                sub_l10npack_diff.id = path[0]
                self.packages[path[0]] = {'package':sub_l10npack_diff, 'type':'modified'}
                return sub_l10npack_diff.add_package(l10npack_diff,'/'.join(path[1:]), type)
        return True

    def add_object(self, l10nobject_diff, path=None, type='modified'):
        if path == None or path == '':
            self.objects[l10nobject_diff.id] = {'object':l10nobject_diff, 'type': type}
        else:
            path = path.split('/')
            if path[0] in self.packages:
                self.packages[path[0]]['package'].add_object(l10nobject_diff, '/'.join(path[1:]))
            else:
                sub_l10npack_diff = L10nPackageDiff()
                sub_l10npack_diff.id = path[0]
                self.packages[path[0]] = {'package': sub_l10npack_diff, 'type': 'modified'}
                return sub_l10npack_diff.add_object(l10nobject_diff, '/'.join(path[1:]), type)
        return True

    def remove_package(self,path):
        path = path.split('/')
        if len(path)==1:
            if path[0] in self.packages:
                del self.packages[path[0]]
                return True
        else:
            if path[0] in self.packages:
                return self.packages[path[0]]['package'].remove_package('/'.join(path[1:]))
        return False

    def remove_object(self,path):
        path = path.split('/')
        if len(path)==1:
            if path[0] in self.objects:
                del self.objects[path[0]]
                return True
        else:
            if path[0] in self.packages:
                return self.packages[path[0]]['package'].remove_object('/'.join(path[1:]))
        return False

    def get_element(self, path):
        if not path:
            return self
        elem = None
        elems = path.split('/')
        if len(elems) == 0:
            return self

        if len(elems) == 1:
            if elems[0] in self.packages:
                elem = self.packages[elems[0]]['package']
            else:
                if elems[0] in self.objects:
                    elem = self.objects[elems[0]]['object']
            return elem
        else:
            if elems[0] in self.packages:
                return self.packages[elems[0]]['package'].get_element('/'.join(elems[1:]))
            else:
                return None

    def get_packages(self, type='all'):
        if type is 'all':
            return [self.packages[package]['package'] for package in self.packages]
        elif isinstance(type,tuple):
            return [self.packages[package]['package'] for package in self.packages if self.packages[package]['type'] in type]
        else:
            return [self.packages[package]['package'] for package in self.packages if self.packages[package]['type']==type]
    
    def get_objects(self, type='all', recursive=False):
        if type is 'all':
            elems = [self.objects[object]['object'] for object in self.objects]
        elif isinstance(type,tuple):
            elems = [self.objects[object]['object'] for object in self.objects if self.objects[object]['type'] in type]
        else:
            elems = [self.objects[object]['object'] for object in self.objects if self.objects[object]['type']==type]
        if recursive:
            for i in self.packages:
                elems.extend(self.packages[i].get_objects(type=type, recursive=recursive))
        return elems

    def has_object(self, id, type='all'):
        if id in self.objects:
            if type is 'all' or self.objects[id]['type'] is type:
                return True
        return False

    def has_package(self, id, type='all'):
        if id in self.packages:
            if type is 'all' or self.packages[id]['type'] is type:
                return True
        return False

    def get_object(self, id, type='all'):
        if id in self.objects:
            if type is 'all' or self.objects[id]['type'] is type:
                return self.objects[id]['object']
        raise KeyError('No such object: '+id)

    def get_package(self, id, type='all'):
        if id in self.packages:
            if type is 'all' or self.packages[id]['type'] is type:
                return self.packages[id]['package']
        raise KeyError('No such package: '+id)

    def get_object_type(self, id):
        if id in self.objects:
                return self.objects[id]['type']
        return False

    def get_package_type(self, id):
        if id in self.packages:
                return self.packages[id]['type']
        return False

def l10npackage_diff (self, l10npack, flags=None, values=True):
    if flags == None:
        flags = ['added','removed','modified']
    l10npackage_diff = L10nPackageDiff()
    l10npackage_diff.id = self.id
    l10npackage_diff.uri = (self.uri, l10npack.uri)
    packages1 = self.get_packages(names=True)
    packages2 = l10npack.get_packages(names=True)
    object_list1 = self.get_objects(names=True)
    object_list2 = l10npack.get_objects(names=True)

    isect = intersect(packages1, packages2)
    if 'removed' in flags:
        for item in packages1:
            if item not in isect:
                l10npackage_diff.add_package(self.get_package(item), type='removed')
    if 'added' in flags:
        for item in packages2:
            if item not in isect:
                l10npackage_diff.add_package(l10npack.get_package(item), type='added')
    if 'modified' in flags or 'unmodified' in flags:
        for item in isect:
            l10npackage_diff2 = self.packages[item].diff(l10npack.packages[item], flags=flags, values=values)
            if not l10npackage_diff2.empty():
                l10npackage_diff.add_package(l10npackage_diff2, type='modified')
    isect = intersect(object_list1, object_list2)
    if 'removed' in flags:
        for item in object_list1:
            if item not in isect:
                l10npackage_diff.add_object(self.get_object(item), type='removed')
    if 'added' in flags:
        for item in object_list2:
            if item not in isect:
                l10npackage_diff.add_object(l10npack.get_object(item), type='added')
    if 'modified' in flags or 'unmodified' in flags:
        for item in isect:
            l10nobject_diff = self.objects[item].diff(l10npack.objects[item], flags=flags, values=values)
            if not l10nobject_diff.empty():
                l10npackage_diff.add_object(l10nobject_diff, type='modified')
    return l10npackage_diff

L10nPackage.diff = l10npackage_diff

def l10npackage_apply_diff (self, l10npackage_diff):
    for key, item in l10npackage_diff.packages.items():
        if item['type']=='added':
            self.add_package(item['package'])
        elif item['type']=='removed':
            self.remove_package(key)
        elif item['type']=='modified':
            package = self.get_package(key)
            package.apply_diff(item['package'])
    for key, item in l10npackage_diff.objects.items():
        if item['type']=='added':
            self.add_object(item['object'])
        elif item['type']=='removed':
            self.remove_object(key)
        elif item['type']=='modified':
            object = self.get_object(key)
            object.apply_diff(item['object'])

L10nPackage.apply_diff = l10npackage_apply_diff

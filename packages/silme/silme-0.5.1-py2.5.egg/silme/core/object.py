from silme.core.entity import Entity, EntityList


class Blob(object):
    uri = None
    id = None
    source = None


class L10nObject(list, Blob):
    process_function = None
    fallback = None

    def __init__(self, id=None):
        """
        L10nObject can be initialized with optional argument: id
        """
        list.__init__(self)
        Blob.__init__(self)
        self.id = id

    def _get_pos(self, pos):
        """
        It is an internal method for translating tuple in form of:
        ('before', 'entity.id') or ('after', 'entity.id')
        which are returned internally by our methods into a solid number.
        
        If pos is a number it will just be returned as integer.
        """
        if isinstance(pos, tuple):
            p = self.get_entity_pos(pos[1])
            return p + 1 if pos[0] == 'after' else p
        else:
            return int(pos)

    def add_at_pos(self, element, pos=None):
        """
        adds an element to L10nObject.
        pos - if given, allows you to decide where the element will be added
           pos may be in form of an integer or a tuple like ('before', 'entity.id'), ('after', 'entity.id')
        """
        if pos == None:
            self.append(element)
        else:
            self.insert(self._get_pos(pos), element)

    def add_entity(self, entity, pos=None):
        """
        adds an entity to L10nObject
        pos - if given, allows you to decide where the entity will be added
        """
        self.add_at_pos(entity, pos)
        return 1

    def get_value(self, id, fallback=None):
        """
        returns a value of an entity with given id
        fallback - if given overrides default locale fallback (e.g. ['de', 'fr', 'en-US'])
        
        if given entity does not exist it will raise a KeyError
        """
        if fallback == None and self.fallback:
            fallback = self.fallback
        return self.get_entity(id).get_value(fallback)

    def get_locale_codes(self):
        """
        returns list of locale codes existing in L10nObject
        """
        locales = []
        for entity in self.get_entities():
            for key in entity._value.keys():
                if key not in locales:
                    locales.append(key)
        return locales

    def get_entity_ids(self):
        """
        returns list of id's of entities in L10nObject
        """
        return [item.id for item in self if isinstance(item, Entity)]

    def get_entities(self):
        """
        returns all entities from L10nObject
        """
        return [item for item in self if isinstance(item, Entity)]

    def has_entity(self, id):
        """
        returns True if entity with given id exists or False otherwise
        """
        for item in self:
            if isinstance(item, Entity) and item.id == id:
                return True
        return False

    def modify_entity(self, id, value, code=None):
        """
        modifies entity value
        code - if given modified the value for given locale code
        """
        for item in self:
            if isinstance(item, Entity) and item.id == id:
                item.set_value(value, code)
                return True
        raise KeyError('No such entity')

    def get_entity(self, id):
        """
        returns an entity for a given id
        """
        for item in self:
            if isinstance(item, Entity) and item.id == id:
                return item
        raise KeyError('No such entity')

    def get_entity_pos(self, id):
        """
        returns position of entity in L10nObject
        """
        for (i, item) in enumerate(self):
            if isinstance(item, Entity) and item.id == id:
                return i
        raise KeyError('No such entity')

    def remove_entity(self, id):
        """
        removes entity for given id or raises KeyError
        """
        for (num, item) in enumerate(self):
            if isinstance(item, Entity) and item.id == id:
                del self[num]
                return True
        raise KeyError('No such entity')

    def set_fallback(self, fallback):
        self.fallback = fallback

    def add_comment(self, comment, pos=None):
        self.add_at_pos(comment, pos)
        return 1

    def add_string(self, string, pos=None):
        self.add_at_pos(string, pos)
        return 1

    def add_element(self, element, pos=None):
        """
        adds an element (string, entity or comment) to l10nObject
        pos - if given addes an element at given position
        
        returns a number representing how many new elements have been added
          Usually one, but if a new string gets added and is concatanated to previous/next one
          the value will be 0.
        """
        if element == None:
            return 0
        t = type(element).__name__[0]
        if t == 's' or t == 'u': # s - str, u - unicode
            return self.add_string(element, pos)
        elif t == 'E': # E - Entity
            return self.add_entity(element, pos)
        elif t == 'C': # C - Comment
            return self.add_comment(element, pos)
        else:
            raise Exception('Cannot add element of type "' + type(element).__name__ +
                            '" to L10nObject')

    def add_elements(self, sequence, pos=None):
        """
        adds set of elements
        pos - if given addes the elements at given position
        
        returns a number representing how many new elements have been added
          Usually the number will be equal the number of 
        """
        it = iter(sequence)
        tshift = 0
        if not pos == None:
            pos = self._get_pos(pos)
        while True:
            try:
                shift = self.add_element(it.next(), pos=(None if pos == None else pos+tshift))
                tshift += shift
            except StopIteration:
                break
        return tshift

    def remove_element(self, pos):
        """
        removes an element at given position from the L10nObject
        """
        del self[pos]

    def get_element(self, position):
        return self[position]

    def get_entitylist(self):
        """
        returns an ElementList representation of the L10nObject
        """
        entityList = EntityList()
        entityList.id = self.id
        entityList.fallback = self.fallback
        for entity in self.get_entities():
            entityList.add_entity(entity)
        return entityList

    def process(self):
        """
        launches a process function on the L10nObject if
        processing method is provided
        """
        return self.process_function(self)

    def get_locales(self, localelist):
        """
        returns a clone of L10nObject with entities only
        in given list of locales
        """
        l10n_object = L10nObject()
        l10n_object.id = self.id
        l10n_object.uri = self.uri
        l10n_object.fallback = localelist
        l10n_object.source = self.source
        for element in self:
            if isinstance(element, Entity):
                l10n_object.add_entity(element.get_locales(localelist))
            else:
                l10n_object.add_element(element)
        return l10n_object

    def merge(self, l10n_object):
        """
        merges L10nObject with another L10nObject (only entities)
        """
        for entity in l10n_object.get_entities():
            if self.has_entity(entity.id):
                self.get_entity(entity.id).merge(entity)
            else:
                self.add_entity(entity)
        if l10n_object.fallback:
            for code in l10n_object.fallback:
                if code not in self.fallback:
                    self.fallback.append(code)


class Comment(L10nObject):
    """
    Comment class is a sub-class of L10nObject but cannot
    take Comment as an element.
    
    It means that by default Comments store strings and Entities.
    """
    def __init__(self, elist=None):
        L10nObject.__init__(self)
        if elist:
            for i in elist:
                self.add_element(i)

    def add_element(self, element, pos=None):
        if isinstance(element, Comment):
            raise Exception('Cannot add comment to comment')
        return L10nObject.add_element(self, element, pos)


class L10nPackage(object):
    """
    L10nPackage is a container object that stores
    set of objects (L10nobject or Object) and sub-l10npackages.
    
    It's easiest to think of it as a filesystem directory that
    can store files and nested directories.
    It abstracts the package from the file system, so once you load
    L10nPackage into memory you can serialize it, send it, save as .zip file or
    simply diff.
    """
    uri = None

    def __init__(self, id=None):
        self.objects = {}
        self.packages = {}
        self.id = id

    def add_object(self, object, path=None):
        """
        Adds an object to L10nPackage.
        
        Optional parameter path allows to declare place
        inside the package where the object should be added.
        
        For example l10npack.add_object(l10nobject, 'pkg1/pkg2') is similar to
        l10npack.get_package('pkg1').get_package('pkg2').add_object(l10nobject)
        with the difference that it will create missing sub packages.
        """
        if path == None or path == '':
            self.objects[object.id] = object
        else:
            path = path.split('/')
            if path[0] in self.packages:
                self.packages[path[0]].add_object(object, '/'.join(path[1:]))
            else:
                sub_l10n_pack = L10nPackage()
                sub_l10n_pack.id = path[0]
                self.add_package(sub_l10n_pack)
                sub_l10n_pack.add_object(object, '/'.join(path[1:]))

    def add_package(self, l10npackage, path=None):
        """
        Adds a package to L10nPackage.
        
        Optional parameter path allows to declare place
        inside the package where the subpackage should be added.
        
        For example l10npack.add_package(subl10npack, 'pkg1/pkg2') is similar to
        l10npack.get_package('pkg1').get_package('pkg2').add_package(subl10npack)
        with the difference that it will create missing sub packages.
        """
        if path == None or path == '':
            self.packages[l10npackage.id] = l10npackage
        else:
            path = path.split('/')
            if path[0] in self.packages:
                self.packages[path[0]].add_package(l10npackage, '/'.join(path[1:]))
            else:
                sub_l10n_pack = L10nPackage()
                sub_l10n_pack.id = path[0]
                self.packages[path[0]] = sub_l10n_pack
                sub_l10n_pack.add_package(l10npackage,'/'.join(path[1:]))

    def get_packages(self, names=False):
        """
        Returns a list of packages inside L10nPackage.
        If parameter names is set to True list of
        names is returned instead of objects.
        """
        if names == True:
            return self.packages.keys()
        else:
            return self.packages.values()

    def get_objects(self, type='all', names=False):
        """
        Returns a list of objects inside L10nPackage.
        If parameter names is set to True list of
        names is returned instead of objects.
        """
        if type == 'all':
            if names == True:
                return self.objects.keys()
            else:
                return self.objects.values()
        else:
            l10n_objects = {}
            if type == 'entitylist':
                type = EntityList
            elif type == 'l10nobject':
                type = L10nObject
            elif type == 'object':
                type = Object
            for object in self.objects:
                if isinstance(self.objects[object], type):
                    l10n_objects[object] = self.objects[object] 
            if names == True:
                return l10n_objects.keys()
            else:
                return l10n_objects.values()

    def get_entities(self, recursive=True):
        """
        Returns a list of all entities inside the L10nPackage
        
        If optional parameter recursive is set to True it will
        return all packages from this package and its subpackages.
        """
        entities = []
        if recursive:
            for pack in self.packages.values():
                entities.extend(pack.get_entities())
        for i in self.objects:
            if isinstance(self.objects[i], L10nObject):
                entities.extend(self.objects[i].get_entities())
            elif isinstance(self.objects[i], EntityList):
                entities.extend(self.objects[i].values())
        return entities

    def has_object(self, id):
        return id in self.objects

    def has_package(self, id):
        return id in self.packages

    def get_object(self, id):
        if id in self.objects:
            return self.objects[id]
        raise KeyError('No such object')
        
    def get_package(self, id):
        if id in self.packages:
            return self.packages[id]
        raise KeyError('No such package')

    def get_element(self, path):
        """
        Returns an element from inside L10nPackage
        by its path.
        
        l10npack.get_element('pkg1/pkg2/object.po') will return
        the same as
        l10npack.get_package('pkg1').get_package('pkg2').get_object('object.po')
        
        IF the path is empty the result will be None
        """
        if not path:
            return None
        elems = path.split('/')
        if len(elems) == 0:
            return None

        if len(elems) == 2 and elems[1] == '':
            elems = elems[:-1]

        if len(elems) == 1:
            if self.has_package(elems[0]):
                elem = self.get_package(elems[0])
            elif self.has_object(elems[0]):
                elem = self.get_object(elems[0])
            else:
                return None
            return elem
        else:
            if self.packages.has_key(elems[0]):
                return self.packages[elems[0]].get_element('/'.join(elems[1:]))
            else:
                return None

    def remove_object(self, id):
        del self.objects[id]
        
    def remove_package(self, id):
        del self.packages[id]

    def get_value(self, path, entity):
        elem = self.get_element(path)
        return elem.get_value(entity)

    def merge(self, l10n_package):
        for id in l10n_package.objects:
            object2 = l10n_package.get_object(id)
            if self.has_object(id):
                object = self.get_object(id)
                if type(object) is not type(object2):
                    raise Exception('Object type mismatch! (' + id + ': ' +
                                    type(object) + ',' + type(object2) + ')')
                elif not isinstance(object, EntityList):
                    self.add_object(object2)
                else:
                    object.merge(object2)
            else:
                self.add_object(object2)
        for id in l10n_package.packages:
            package = l10n_package.get_package(id)
            if self.has_package(id):
                self.get_package(id).merge(package)
            else:
                self.add_package(package)

    def get_locales(self, localelist):
        l10n_package = L10nPackage()
        l10n_package.id = self.id
        l10n_package.uri = self.uri
        for object in self.objects.values():
            l10n_package.add_object(object.get_locales(localelist))
        for package in self.packages.values():
            l10nPackage.add_package(package.get_locales(localelist))
        return l10n_package

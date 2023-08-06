"""
silme.core.Entity represents single key:value pair (with possibility og having different values for different locale codes)
silme.core.EntityList is a list of entities.
"""

class Entity(object):
    default_code = None

    def __init__(self, id, value=None, code='default'):
        """
        It is possible to initialize Entity only with id:
        Entity('id')
        
        or giving an initial value (and optionally locale_code):
        Entity('id', 'value'[, 'ab-CD'])
        """
        self.id = id
        self.params = {}
        if value is not None:
            self.default_code = code
            self._value = {code: value}
        else:
            self._value = {}

    def __getattribute__(self, key):
        """Returns a value for given locale: entity['ab-CD']."""
        if key == 'value':
            try:
                return self._value[self.default_code]
            except:
                raise ValueError('Entity has no value')
        else:
          return super(Entity, self).__getattribute__(key)

    #def __setattr__(self, key, value):
    #    if key == 'value':
    #        print self._value
    #        self._value['default'] = value

    def __repr__(self):
        """Prints entity debug text representation."""
        if len(self._value) == 0:
            return '<entity: "%s">' % self.id
        elif len(self._value) == 1:
            if self.default_code == 'default':
                return '<entity: "%s", value: "%s">' % (self.id, self.get_value())
            else:
                return '<entity: "%s", value[%s]: "%s">' % \
                        (self.id, self.default_code, self.get_value())
        else:
            keys = self._value.keys()
            l = len(self.default_code)
            string = '<entity: "%s", value[%s]: "%s",\n' % \
                    (self.id, self.default_code, self.get_value())
            while len(keys):
                i = keys.pop()
                if not i == self.default_code:
                    string += ' '*(18 + len(self.id) + l - len(i)) + \
                            '[%s]: "%s"' % (i, self._value[i])
                    if len(keys):
                        string += ',\n'
                    else:
                        string += '>'
            return string

    def __delitem__(self, code):
        """Deletes value in given locale: del entity['ab-CD']."""
        del self._value[code]
        if self.default_code == code:
            try:
                self.default_code = self._value.keys()[0]
            except:
                self.default_code = None
    
    def __getitem__(self, code): return self._value[code]
    
    def __setitem__(self, code, value): self.set_value(value, code)
    
    def set_default_code(self, code):
        """Overwrites default code."""
        self.default_code = code

    def get_default_code(self):
        """Returns default locale code for Entity."""
        return self.default_code

    def set_value(self, value, code=None):
        """Sets an entity value in given locale code.
        If not locale code is given, the default is 'default'."""
        if code:
            if not self.default_code:
                self.default_code = code
        else:
            if not self.default_code:
                self.default_code = 'default'
            code = self.default_code
        self._value[code] = value
    
    def get_value(self, fallback=None):
        """Returns entity value.
        
        fallback options makes it possible to declare a list of
        optional codes to try in the order.
        If not fallback is declared default code is used.
        
        Raises KeyError in case no code will work."""
        try:
            return self._value[fallback]
        except:
            if not fallback:
                if not self._value:
                    return u''
                return self._value[self.default_code]
            else:
                for code in fallback:
                    try:
                        return self._value[code]
                    except:
                        pass
                raise KeyError()

    def get_value_with_code(self, fallback=None):
        """Returns entity value together with used locale_code
        in form of tuple (value, code).
        
        fallback options makes it possible to declare a list of
        optional codes to try in the order.
        If not fallback is declared default code is used.
        
        Raises KeyError in case no code will work."""
        try:
            return (self._value[fallback], fallback)
        except:
            if not fallback:
                return (self._value[self.default_code], None)
            else:
                for code in fallback:
                    try:
                        return (self._value[code], code)
                    except:
                        pass
                raise KeyError()

    def remove_value(self, code):
        """Removes value from entity.
        
        It also clears default_code to first available or None.
        """
        del self._value[code]
        if self.default_code == code:
            try:
                self.default_code = self._value.keys()[0]
            except:
                self.default_code = None

    def get_locale_codes(self):
        """Returns list of all locale codes available in this entity."""
        return self._value.keys()

    def get_locales(self, localelist):
        """Returns new Entity with locales filtered by
        localelist argument of locale codes."""
        entity = Entity(self.id)
        entity.params = self.params
        for (key, value) in self._value.items():
            if key in localelist:
                if not entity.default_code:
                    entity.default_code = key
                entity._value[key] = value
        return entity

    def merge(self, entity):
        """Merges entity with another by adding and
        overwriting all values from argument."""
        for (key, value) in entity._value.items():
            self.set_value(value, key)


class EntityList(dict):
    uri = None
    id = None
    _keys = None

    def __init__(self, id=None, elist=None, order=True):
        """
        id - id for EntityList
        list - list of entities to add to EntityList
        order - if EntityList should keep entities order according to the order
                in which they were added
        """
        dict.__init__(self)
        self.fallback = []
        if id:
            self.id = id
        if elist:
            if isinstance(elist, list):
                map(self.add_entity, elist)
            elif isinstance(elist, dict):
                map(self.add_entity, elist.values())
            else:
                raise ValueError('could not assign list')
        if order:
            self._keys = []

    def add_entity(self, entity):
        """Adds new entity to EntityList"""
        self[entity.id] = entity
        if not self._keys is None:
            self._keys.append(entity.id)

    def get_entities(self):
        """Returns a list of all entities from EntityList."""
        if self._keys is None:
            return self.values()
        else:
            return [self[i] for i in self._keys]

    def get_entity_ids(self):
        """Returns all entity ids from EntityList."""
        if self._keys is None:
            return self.keys()
        else:
            return self._keys

    def has_entity(self, id):
        """Returns bool result of testing if entity with given id is in EntityList."""
        return self.has_key(id)

    def modify_entity(self, id, value, code='default'):
        """Modifies entity value in EntityList, optionally with given locale code."""
        self[id].set_value(value, code)
        return True

    def get_entity(self, id):
        """Returns entity with given id."""
        return self[id]

    def remove_entity(self, id):
        """Removes entity with given id from EntityList."""
        del self[id]
        if not self._keys is None:
            self._keys.remove(id)

    def get_value(self, id, fallback=None):
        """Returns entity value from EntityList.
        
        fallback -- list of locale codes to try when getting value from entity.
        """
        if fallback == None and self.fallback:
            return self[id].get_value(self.fallback)
        return self[id].get_value(fallback)

    def get_locale_codes(self):
        """Returns list of locale codes existing in entities in EntityList."""
        locales = []
        for entity in self.values():
            for key in entity.value.keys():
                if key not in locales:
                    locales.append(key)
        return locales

    def set_fallback(self, fallback):
        """Defines locale code fallback list for EntityList."""
        self.fallback = fallback

    def get_locales(self, localelist):
        """Returns a new EntityList filtered to entities with locale codes listed in localelist argument."""
        elist = EntityList()
        elist.id = self.id
        elist.uri = self.uri
        elist._keys = self._keys
        elist.fallback = self.fallback
        for entity in self.values():
            elist.add_entity(entity.get_locales(localelist))
        return elist

    def merge(self, elist):
        """Merges one EntityList with another."""
        for entity in elist:
            if self.has_key(entity.id):
                self[entity.id].merge(entity)
            else:
                self[entity.id] = entity

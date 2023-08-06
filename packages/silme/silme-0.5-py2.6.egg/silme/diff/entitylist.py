from silme.core.entity import EntityList, Entity

def intersect(a, b):
    """ returns what's in both a and b """
    return list(set(a) & set(b))

def difference(a, b):
    """ returns what's in b and not in a """
    return list(set(b).difference(set(a))) 

class EntityListDiff(dict):
    def __init__(self):
        self.id = None
        self.uri = None

    def empty(self):
        return not bool(len(self))

    # pos - may be a number or a tuple ('after','id') or ('before','id')
    def add(self, flag, entity, id, pos=None):
        self[id] = {'elem': entity, 'flags': [flag], 'pos':pos}

    def remove(self, id):
        if id in self:
            del self[id]

    def get_entity(self, id):
        try:
            return self[id]['elem']
        except KeyError:
            raise KeyError('No such id: '+id)

    def get_entities(self, type='all'):
        entities = {}
        for item in self.values():
            if type=='all' or type in item['flags']:
                if isinstance(item['elem'], Entity):
                    item['elem'].params['diff_flags'] = item['flags']
                entities[item['elem'].id] = item['elem']
        return entities

def entitylist_diff (self, entitylist, flags=None, values=True):
    if flags == None:
        flags = ['added','removed','modified']
    entitylistdiff = EntityListDiff()
    entitylistdiff.id = self.id
    entitylistdiff.uri = (self.uri, entitylist.uri)
    entities1 = self.get_entity_ids()
    entities2 = entitylist.get_entity_ids()

    isect = intersect(entities1, entities2)
    if 'removed' in flags:
        for item in difference(isect, entities1):
            entitylistdiff.add('removed', id=item, entity=self[item])
    if 'added' in flags:
        for item in difference(isect, entities2):
            entitylistdiff.add('added', id=item, entity=entitylist[item])

    if ('modified' in flags and values is True) or ('unmodified' in flags):
        for item in isect:
            if values is False:
                entitylistdiff.add('unmodified', id=item, entity=self[item])
            else:
                entity = self[item]
                entity2 = entitylist[item]
                entitydiff = entity.diff(entity2)
                if entitydiff.empty():
                    if 'unmodified' in flags:
                        entitylistdiff.add('unmodified', id=item, entity=entity)
                else:
                    if 'modified' in flags:
                        entitylistdiff.add('modified', id=item, entity=entitydiff)
    return entitylistdiff

EntityList.diff = entitylist_diff

def entitylist_apply_diff (self, entitylistdiff):
    for key, item in entitylistdiff.items():
        if 'removed' in item['flags']:
            self.remove_entity(key)
        elif 'modified' in item['flags']:
            self.get_entity(key).apply_diff(item['elem'])
        elif 'added' in item['flags']:
            if isinstance(item['elem'], tuple):
                self.add_entity(item['elem'][0], pos=item['elem'][1])
            else:
                self.add_entity(item['elem'])

EntityList.apply_diff = entitylist_apply_diff

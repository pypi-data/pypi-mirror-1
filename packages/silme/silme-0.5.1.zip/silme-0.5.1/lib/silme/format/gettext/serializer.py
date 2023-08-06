from silme.core.entity import EntityList, Entity
from silme.core.object import Comment

import re

class GettextSerializer:
    @classmethod
    def serialize(cls, l10nobject, fallback=None):
        if not fallback:
            fallback = l10nobject.fallback
        string = u''.join([cls.dump_element(element, fallback) for element in l10nobject])
        return string

    @classmethod
    def dump_element (cls, element, fallback=None):
        if isinstance(element, Entity):
            return cls.dump_entity(element, fallback=fallback)
        elif isinstance(element,Comment):
            return cls.dump_comment(element)
        else:
            return element

    @classmethod
    def dump_entity (cls, entity, fallback=None):
        string = u'msgid '+entity.id+u'\nmsgstr "'+entity.get_value(fallback)+u'"\n'
        return string

    @classmethod
    def dump_entitylist(cls, elist, fallback=None):
        if not fallback:
            fallback = elist.fallback
        string = u''.join([cls.dump_entity(entity, fallback)+'\n' for entity in elist.get_entities()])
        return string

    @classmethod
    def dump_comment (cls, comment):
        string = u''
        for element in comment:
            string += cls.dump_element(element)
        if string:
            pattern = re.compile('\n')
            string = pattern.sub('\n#', string)
            string = '#' + string
            if string.endswith('#'):
                string = string[:-1]
        return string

from silme.core.entity import EntityList, Entity
from structure import *
from parser import HTMLParser as Parser

class HTMLSerializer():
    @classmethod
    def serialize(cls, l10nobject, fallback=None):
        raise NotImplementedError()

    @classmethod
    def dump_element (cls, element, fallback=None):
        raise NotImplementedError()

    @classmethod
    def dump_entity (cls, entity, fallback=None):
        raise NotImplementedError()

    @classmethod
    def dump_entitylist(cls, elist, fallback=None):
        raise NotImplementedError()

    @classmethod
    def dump_comment (cls, comment):
        raise NotImplementedError()

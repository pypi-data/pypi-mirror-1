from parser import GettextParser as Parser
from structure import GettextStructure as Structure
from serializer import GettextSerializer as Serializer

class GettextFormatParser():
    name = 'gettext'
    desc = "GetText format parser"
    extensions = ['po']
    encoding = None # allowed encoding
    fallback = None

    @classmethod
    def dump_l10nobject (cls, l10nobject):
        text = Serializer.serialize(l10nobject)
        return text

    @classmethod
    def dump_entitylist (cls, elist):
        text = Serializer.dump_entitylist(elist)
        return text

    @classmethod
    def get_entitylist (cls, text, code='default'):
        l10nobject = Parser.parse_to_entitylist(text, code=code)
        return l10nobject

    @classmethod
    def get_l10nobject (cls, text, code='default'):
        l10nobject = Parser.parse(text, code=code)
        return l10nobject

def register(Manager):
    Manager.register(GettextFormatParser)

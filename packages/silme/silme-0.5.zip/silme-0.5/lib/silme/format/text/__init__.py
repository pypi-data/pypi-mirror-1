from serializer import TextSerializer as Serializer

class TextFormatParser():
    name = 'text'
    desc = 'Text writer'
    extensions = ['text']
    encoding = 'utf_8' # allowed encoding
    fallback = None
    
    @classmethod
    def dump_l10nobject (cls, l10nobject):
        text = Serializer.serialize(l10nobject)
        return text

    @classmethod
    def dump_l10npackage (cls, l10npack):
        text = Serializer.serialize(l10npack)
        return text


    @classmethod
    def dump_entitylistdiff (cls, entitylistdiff):
        text = Serializer.dump_entitylistdiff(entitylistdiff)
        return text

    @classmethod
    def dump_l10nobjectdiff (cls, l10nobjectdiff):
        text = Serializer.dump_l10nobjectdiff(l10nobjectdiff)
        return text

    @classmethod
    def dump_l10npackagediff (cls, l10npackagediff):
        text = Serializer.dump_l10npackagediff(l10npackagediff)
        return text

    @classmethod
    def dump_entitylist (cls, entitylist):
        text = Serializer.serialize(entitylist)
        return text

def register(Manager):
    Manager.register(TextFormatParser)
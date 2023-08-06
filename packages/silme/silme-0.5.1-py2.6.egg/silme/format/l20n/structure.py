from silme.core.object import L10nObject

class LOL(L10nObject):
    def __init__(self):
        self.structure = []

    def add(self, element):
        if element != None:
            self.structure.append(element)
    
    def get_entities(self):
        entities = []
        for element in self.structure:
            if isinstance(element, Entity):
                entities.append(element)
        return entities

class WS():
    def __init__(self, content):
        self.content = content

class Group():
    def __init__(self):
        self.structure = []

    def add(self, entry):
        self.structure.append(entry)

class Entity():
    def __init__(self):
        self.id = None
        self.value = None
    
    def get_value(self):
        if isinstance(self.value, String):
            return self.value.buffer
        else:
            return ''

class Comment():
    def __init__(self, content=None):
        self.content = content

class Expression():
    pass

class Index():
    def __init__(self):
        self.expression = None

class String():
    def __init__(self):
        self.buffer = ''
    pass

class Array():
    def __init__(self):
        self.values = []

class Hash():
    def __init__(self):
        self.key_value_pairs = {}

class Expander():
    pass

class Macro():
    def __init__(self):
        self.structure=[]

class Operator(str):
    pass

class KeyValuePair():
    def __init__(self):
        self.key = None
        self.value = None
        self.ws = []
        

class OperatorExpression(list):
    pass

class ConditionalExpression(OperatorExpression):
    pass

class OrExpression(OperatorExpression):
    pass

class AndExpression(OperatorExpression):
    pass

class EqualityExpression(OperatorExpression):
    pass

class RelationalExpression(OperatorExpression):
    pass

class AdditiveExpression(OperatorExpression):
    pass

class MultiplicativeExpression(OperatorExpression):
    pass

class UnaryExpression(OperatorExpression):
    pass

class BraceExpression(list):
    pass

class MacroCall():
    def __init__(self):
        self.structure=[]

class Idref(list):
    pass


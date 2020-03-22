class SymbolTable:
    def __init__(self):
        self.staticCount = 0
        self.fieldCount = 0
        self.argCount = 0
        self.varCount = 0
        self.ty = ''
        self.kind = ''
        self.classTable = {}
        self.symbolTable = {}

    def startSubroutine(self):
        self.symbolTable = {}
        self.argCount = 0
        self.varCount = 0

    def preDefine(self, element, char):
        if char == 'type':
            self.ty = element
        elif char == 'kind':
            self.kind = element
        elif char == 'name':
            self.Define(element, self.ty, self.kind)

    def Define(self, name, ty, kind):
        if kind == 'static':
            self.classTable[name] = (ty, kind, self.staticCount)
            self.staticCount += 1
        elif kind == 'field':
            self.classTable[name] = (ty, kind, self.fieldCount)
            self.fieldCount += 1
        elif kind == 'arg':
            self.symbolTable[name] = (ty, kind, self.argCount)
            self.argCount += 1
        elif kind == 'var':
            self.symbolTable[name] = (ty, kind, self.varCount)
            self.varCount += 1
        else:
            raise SyntaxError("unvalid kind: " + kind)

    def VarCount(self, kind):
        if kind == 'static':
            return self.staticCount
        elif kind == 'field':
            return self.fieldCount
        elif kind == 'arg':
            return self.argCount
        elif kind == 'var':
            return self.varCount
        else:
            raise SyntaxError("unvalid kind: " + kind)

    def KindOf(self, name):
        if name in self.symbolTable:
            return self.symbolTable[name][1]
        elif name in self.classTable:
            return self.classTable[name][1]
        else:
            return 'none'

    def TypeOf(self, name):
        if name in self.symbolTable:
            return self.symbolTable[name][0]
        elif name in self.classTable:
            return self.classTable[name][0]

    def IndexOf(self, name):
        if name in self.symbolTable:
            return self.symbolTable[name][2]
        elif name in self.classTable:
            return self.classTable[name][2]

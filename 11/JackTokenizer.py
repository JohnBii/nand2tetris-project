class JackTokenizer:
    def __init__(self, name):
        self.f = open(name, 'r')
        self.nextLine = ''
        self.currunToken = ''
        self.nexToken = ''
        self.symboList = [
            '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/',
            '&', '|', '<', '>', '=', '~'
        ]
        self.keywords = [
            'class', 'constructor', 'function', 'method', 'field', 'static',
            'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null',
            'this', 'let', 'do', 'if', 'else', 'while', 'return'
        ]

    def closeFile(self):
        self.f.close()

    def commentStrip(self, s):
        s = s.strip()
        if '//' in s:
            ss = s[:s.index('//')].rstrip()
            return self.commentStrip(ss)
        if '/*' in s and '*/' in s:
            ss = s[:s.index('/*')] + ' ' + s[s.index('*/') + 2:]
            return self.commentStrip(ss)
        if '/*' in s and '*/' not in s:
            ss = s[:s.index('/*')] + ' '
            subs = ''
            while '*/' not in subs:
                subs = self.f.readline()
            ss += subs[subs.index('*/') + 2:]
            return self.commentStrip(ss)
        else:
            return s

    def hasMoreTokens(self):
        if self.nextLine:
            return True
        else:
            self.nextLine = self.f.readline()
            if not self.nextLine:
                return False
            else:
                self.nextLine = self.commentStrip(self.nextLine)
                if not self.nextLine:
                    return self.hasMoreTokens()
                else:
                    return True

    def advance(self):
        if self.nexToken:
            self.currunToken = self.nexToken
            self.nexToken = ''
        else:
            if ' ' in self.nextLine:
                self.currunToken = self.nextLine[:self.nextLine.index(' ')]
                self.nextLine = self.nextLine[self.nextLine.index(' ') +
                                              1:].strip()
            else:
                self.currunToken = self.nextLine
                self.nextLine = ''

    def tokenType(self):
        first = self.currunToken[0]
        if first == '"':
            return "STRING_CONST"
        elif first in self.symboList:
            return "SYMBOL"
        elif first.isdecimal():
            return "INT_CONST"
        else:
            first = ''
            count = 0
            while self.currunToken[count].isalpha():
                first = first + self.currunToken[count]
                count += 1
                if first == self.currunToken:
                    break
            if first in self.keywords:
                return "KEYWORD"
            else:
                return "IDENTIFIER"

    def keyword(self):
        if self.nexToken == '':
            count = 0
            length = len(self.currunToken)
            while count < length and self.currunToken[count].isalpha():
                count += 1
            self.nexToken = self.currunToken[count:]
            self.currunToken = self.currunToken[:count]
        return self.currunToken

    def symbol(self):
        if self.nexToken == '':
            self.nexToken = self.currunToken[1:]
            self.currunToken = self.currunToken[0]
        return self.currunToken

    def identifier(self):
        if self.nexToken == '':
            count = 0
            length = len(self.currunToken)
            while count < length and (self.currunToken[count].isalnum() or
                                      (self.currunToken[count] == '_')):
                count += 1
            self.nexToken = self.currunToken[count:]
            self.currunToken = self.currunToken[:count]
        return self.currunToken

    def intVal(self):
        if self.nexToken == '':
            count = 0
            length = len(self.currunToken)
            while count < length and self.currunToken[count].isdecimal():
                count += 1
            self.nexToken = self.currunToken[count:]
            self.currunToken = self.currunToken[:count]
        intV = int(self.currunToken)
        if 0 <= intV <= 32767:
            return intV
        else:
            raise SyntaxError("number outrange(0-32767): " + str(intV))

    def stringVal(self):
        if '"' in self.currunToken:
            self.currunToken = self.currunToken[1:]
            s = ''
            while not ('"' in self.currunToken):
                s += self.currunToken + ' '
                self.advance()
            s += self.currunToken[:self.currunToken.index('"')]
            self.nexToken = self.currunToken[self.currunToken.index('"') + 1:]
            self.currunToken = s
        return self.currunToken

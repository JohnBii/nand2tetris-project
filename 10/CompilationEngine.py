def wrongE(expect, got):
    raise SyntaxError("expect " + expect + " but got " + got)


class CompilationEngine:
    def __init__(self, tokenizer, outputFile):
        self.indentation = 0
        self.t = tokenizer
        self.oF = outputFile
        self.t.constructor()

    def nextToken(self):
        if self.t.hasMoreTokens():
            self.t.advance()
        else:
            raise SyntaxError("nullError")

    def expect(self, expectType, specifics=(True, )):
        if not self.t.tokenType() == expectType:
            wrongE(str(specifics), self.t.tokenType())
        if expectType == 'SYMBOL':
            spe = self.t.symbol()
        elif expectType == 'KEYWORD':
            spe = self.t.keyword()
        elif expectType == 'IDENTIFIER':
            return self.t.identifier()
        if spe in specifics:
            return spe
        wrongE(str(specifics), spe)

    def writeXML(self, s, writeType='other'):
        for i in range(self.indentation):
            self.oF.write('  ')
        if writeType == 'IDENTIFIER':
            self.oF.write('<identifier> ' + s + ' </identifier>\n')
        elif writeType == 'SYMBOL':
            if s == '<':
                s = '&lt;'
            elif s == '>':
                s = '&gt;'
            elif s == '&':
                s = '&amp;'
            self.oF.write('<symbol> ' + s + ' </symbol>\n')
        elif writeType == 'KEYWORD':
            self.oF.write('<keyword> ' + s + ' </keyword>\n')
        else:
            self.oF.write(s)

    def CompiletypeVar(self):
        # compile var
        # ;;; type varName ( ',' varName)* ';' ;;;
        # ENTRY: Tokenizer positioned brfore type
        # EXIT: Tokenizer positioned on ';'

        # type
        self.nextToken()
        if self.t.tokenType() == 'IDENTIFIER':
            self.writeXML(self.t.identifier(), 'IDENTIFIER')
        else:
            self.expect('KEYWORD', ('int', 'char', 'boolean'))
            self.writeXML(self.t.keyword(), 'KEYWORD')
        # varName
        self.nextToken()
        self.expect('IDENTIFIER')
        self.writeXML(self.t.identifier(), 'IDENTIFIER')
        # (',' varName)*
        while True:
            self.nextToken()
            if self.t.tokenType() == 'SYMBOL' and self.t.symbol() == ';':
                self.writeXML(';', 'SYMBOL')
                break
            else:
                # ','
                self.expect('SYMBOL', ',')
                self.writeXML(',', 'SYMBOL')
                # varName
                self.nextToken()
                self.expect('IDENTIFIER')
                self.writeXML(self.t.identifier(), 'IDENTIFIER')

    def CompileExpressionListBlock(self):
        # Compile expressionList block
        # ;;; '(' expressionList ')' ;;;
        # ENTRY: Tokenizer positioned on '('
        # EXIT: Tokenizer positioned on ')'
        self.expect('SYMBOL', '(')
        self.writeXML('(', 'SYMBOL')
        self.CompileExpressionList()
        self.expect('SYMBOL', ')')
        self.writeXML(')', 'SYMBOL')

    def Compile(self):
        self.nextToken()
        self.CompileClass()

    def CompileClass(self):
        # compile class
        # ;;; 'class' className '{' classVarDec* subroutineDec* '}' ;;;
        # ENTRY: Tokenizer positioned on 'class'
        # EXIT: Tokenizer positioned on '}'

        self.expect('KEYWORD', 'class')
        self.writeXML('<class>\n')
        self.indentation += 1
        # 'class'
        self.writeXML(self.t.keyword(), 'KEYWORD')
        # identifier
        self.nextToken()
        self.expect('IDENTIFIER')
        self.writeXML(self.t.identifier(), 'IDENTIFIER')
        # '{'
        self.nextToken()
        self.expect('SYMBOL', '{')
        self.writeXML('{', 'SYMBOL')
        # classVarDec* and subroutine*
        while True:
            self.nextToken()
            if self.t.tokenType() == 'SYMBOL' and self.t.symbol() == '}':
                break
            elif self.t.tokenType() == 'KEYWORD':
                keyword = self.t.keyword()
                if keyword in ('static', 'field'):
                    self.CompileClassVarDec()
                    continue
                elif keyword in ('constructor', 'function', 'method'):
                    self.CompileSubroutine()
                    continue
            wrongE('classVarDec* and subroutine*', self.t.tokenType())
        # '}'
        self.expect('SYMBOL', '}')
        self.writeXML('}', 'SYMBOL')

        # /class
        self.indentation -= 1
        self.writeXML('</class>\n')

    def CompileClassVarDec(self):
        # classVarDec
        # ;;; ('static'|'field') type varName (',' varName)* ';' ;;;
        # ENTRY: Tokenizer positioned on 'static'|'field'
        # EXIT: Tokenizer positioned on ';'
        self.writeXML('<classVarDec>\n')
        self.indentation += 1

        # static | field
        self.writeXML(self.t.keyword(), 'KEYWORD')
        # typeVar
        self.CompiletypeVar()

        self.indentation -= 1
        self.writeXML('</classVarDec>\n')

    def CompileSubroutine(self):
        # compile subroutineDec
        # ;;; ('constructor'|''function'|'method')
        # ('void'|type) subroutineName '('parameterList')' ;;;
        # subroutineBody
        # Entry: Tokenizer positioned on ('constructor'|''function'|'method')
        # EXIT: Tokenizer positioned on '}'(from subroutineBody)
        self.writeXML('<subroutineDec>\n')
        self.indentation += 1

        # construcor | function | method
        self.writeXML(self.t.keyword(), 'KEYWORD')
        # type
        self.nextToken()
        if self.t.tokenType() == 'IDENTIFIER':
            self.writeXML(self.t.identifier(), 'IDENTIFIER')
        else:
            self.expect('KEYWORD', ('int', 'char', 'boolean', 'void'))
            self.writeXML(self.t.keyword(), 'KEYWORD')
        # subroutineName
        self.nextToken()
        self.expect('IDENTIFIER')
        self.writeXML(self.t.identifier(), 'IDENTIFIER')
        # '('
        self.nextToken()
        self.expect('SYMBOL', '(')
        self.writeXML(self.t.symbol(), 'SYMBOL')
        # parameterList
        self.CompileParameterList()
        # ')'
        self.expect('SYMBOL', ')')
        self.writeXML(self.t.symbol(), 'SYMBOL')

        # subroutineBody
        self.writeXML('<subroutineBody>\n')
        self.indentation += 1

        # {
        self.nextToken()
        self.expect('SYMBOL', '{')
        self.writeXML(self.t.symbol(), 'SYMBOL')
        # varDec*
        while True:
            self.nextToken()
            if self.t.tokenType() == 'KEYWORD' and self.t.keyword() == 'var':
                self.CompileVarDec()
            else:
                break
        # statements
        self.CompileStatementList()
        # }
        self.expect('SYMBOL', '}')
        self.writeXML('}', 'SYMBOL')

        # /subroutineBody
        self.indentation -= 1
        self.writeXML('</subroutineBody>\n')

        # /subroutineDec
        self.indentation -= 1
        self.writeXML('</subroutineDec>\n')

    def CompileParameterList(self):
        # compile parameterList
        # ;;; ((type varName) (',' type varName)*)? ;;;
        # ENTRY: Tokenizer positioned on '('
        # EXIT: Tokenizer positioned on ')'
        self.writeXML('<parameterList>\n')
        self.indentation += 1

        # type
        while True:
            self.nextToken()
            if self.t.tokenType() == 'SYMBOL' and self.t.symbol() == ')':
                break
            elif self.t.tokenType() == 'SYMBOL' and self.t.symbol() == ',':
                # ','
                self.writeXML(',', 'SYMBOL')
                # type
                self.nextToken()
                if self.t.tokenType() == 'IDENTIFIER':
                    self.writeXML(self.t.identifier(), 'IDENTIFIER')
                else:
                    self.expect('KEYWORD', ('int', 'char', 'boolean'))
                    self.writeXML(self.t.keyword(), 'KEYWORD')
                # varName
                self.nextToken()
                self.expect('IDENTIFIER')
                self.writeXML(self.t.identifier(), 'IDENTIFIER')
            else:
                # type
                if self.t.tokenType() == 'IDENTIFIER':
                    self.writeXML(self.t.identifier(), 'IDENTIFIER')
                else:
                    self.expect('KEYWORD', ('int', 'char', 'boolean'))
                    self.writeXML(self.t.keyword(), 'KEYWORD')
                # varName
                self.nextToken()
                self.expect('IDENTIFIER')
                self.writeXML(self.t.identifier(), 'IDENTIFIER')

        self.indentation -= 1
        self.writeXML('</parameterList>\n')

    def CompileVarDec(self):
        # compile VarDec
        # ;;; 'var' type varName (',' varName)* ';' ;;;
        # ENTRY: Tokenizer positioned on 'var'
        # EXIT: Tokenizer positioned on ';'
        self.writeXML('<varDec>\n')
        self.indentation += 1

        self.writeXML('var', 'KEYWORD')
        self.CompiletypeVar()

        # /varDec
        self.indentation -= 1
        self.writeXML('</varDec>\n')

    def CompileStatementList(self):
        # compile statementList
        # ;;; statement* ;;;
        # ENTRY: Tokenizer positioned on statement
        # EXIT: Tokenizer positioned after statement
        self.writeXML('<statementList>\n')
        self.indentation += 1

        while self.t.tokenType() == 'KEYWORD':
            keyword = self.t.keyword()
            if keyword == 'let':
                self.CompileLet()
            elif keyword == 'if':
                self.CompileIf()
            elif keyword == 'while':
                self.CompileWhile()
            elif keyword == 'do':
                self.CompileDo()
            elif keyword == 'return':
                self.CompileReturn()
            else:
                break

        # /statements
        self.indentation -= 1
        self.writeXML('</statementList>\n')

    def CompileDo(self):
        # compile doStatement
        # ;;; 'do' subroutineCall ;;;
        # ENTRY: Tokenizer positioned on 'do'
        # EXIT: Tokenizer positioned after ';'
        self.writeXML('<doStatement>\n')
        self.indentation += 1

        # do
        self.writeXML('do', 'KEYWORD')
        # compile subroutineCall
        # ;;; subroutineName '(' expressionList ')' | (className|varName)
        # '.' subroutineName '(' expressionList ')' ;;;
        # ENTRY: Tokenizer positioned before subroutineName
        # EXIT: Tokenizer positioned on ')'
        # subroutineName or (className|varName)
        self.nextToken()
        self.expect('IDENTIFIER')
        self.writeXML(self.t.identifier(), 'IDENTIFIER')
        self.nextToken()
        if self.t.tokenType() == 'SYMBOL' and self.t.symbol() == '.':
            # '.'
            self.writeXML('.', 'SYMBOL')
            # subroutineName
            self.nextToken()
            self.expect('IDENTIFIER')
            self.writeXML(self.t.identifier(), 'IDENTIFIER')
            # expressionListBlock
            self.nextToken()
            self.CompileExpressionListBlock()
        else:
            self.CompileExpressionListBlock()
        # ;
        self.nextToken()
        self.expect('SYMBOL', ';')
        self.writeXML(';', 'SYMBOL')
        self.nextToken()

        # /doStatement
        self.indentation -= 1
        self.writeXML('</doStatement>\n')

    def CompileLet(self):
        # compile LetStatement
        # ;;; 'let' varName ('[' expression ']')? '=' expression ';' ;;;
        # ENTRY: Tokenizer positioned on 'let'
        # EXIT: Tokenizer positioned after ';'
        self.writeXML('<letStatement>\n')
        self.indentation += 1

        # 'let'
        self.writeXML('let', 'KEYWORD')
        # varName
        self.nextToken()
        self.expect('IDENTIFIER')
        self.writeXML(self.t.identifier(), 'IDENTIFIER')
        # '[' ?
        self.nextToken()
        if self.t.tokenType() == 'SYMBOL' and self.t.symbol() == '[':
            self.writeXML('[', 'SYMBOL')
            # expression
            self.nextToken()
            self.CompileExpression()
            # ']'
            self.expect('SYMBOL', ']')
            self.writeXML(']', 'SYMBOL')
            self.nextToken()
        # '='
        self.expect('SYMBOL', '=')
        self.writeXML('=', 'SYMBOL')
        # expression
        self.nextToken()
        self.CompileExpression()
        # ';'
        self.expect('SYMBOL', ';')
        self.writeXML(';', 'SYMBOL')
        self.nextToken()

        # /letStatements
        self.indentation -= 1
        self.writeXML('</letStatement>\n')

    def CompileWhile(self):
        # compile whileStatement
        # ;;; 'while' '(' expression ')' '{' statements '}' ;;;
        # ENTRY: Tokenizer positioned on 'while'
        # EXIT: Tokenizer positioned after '}'
        self.writeXML('<whileStatement>\n')
        self.indentation += 1

        # while
        self.writeXML('while', 'KEYWORD')
        # (
        self.nextToken()
        self.expect('SYMBOL', '(')
        self.writeXML('(', 'SYMBOL')
        # expression
        self.nextToken()
        self.CompileExpression()
        # )
        self.expect('SYMBOL', ')')
        self.writeXML(')', 'SYMBOL')
        # {
        self.nextToken()
        self.expect('SYMBOL', '{')
        self.writeXML('{', 'SYMBOL')
        # statementList
        self.nextToken()
        self.CompileStatementList()
        # }
        self.expect('SYMBOL', '}')
        self.writeXML('}', 'SYMBOL')
        self.nextToken()

        # /whileStatement
        self.indentation -= 1
        self.writeXML('</whileStatement>\n')

    def CompileReturn(self):
        # compile return
        # ;;; 'return' expression? ';' ;;;
        # ENTRY: Tokenizer positioned on 'return'
        # EXIT: Tokenizer positioned after ';'
        self.writeXML('<returnStatement>\n')
        self.indentation += 1

        # return
        self.writeXML('return', 'KEYWORD')
        # expression?
        self.nextToken()
        if self.t.tokenType() == 'SYMBOL' and self.t.symbol() == ';':
            self.writeXML(';', 'SYMBOL')
        else:
            self.CompileExpression()
            self.expect('SYMBOL', ';')
            self.writeXML(';', 'SYMBOL')
        self.nextToken()

        # /returnStatement
        self.indentation -= 1
        self.writeXML('</returnStatement>\n')

    def CompileIf(self):
        # compile if
        # ;;; 'if' '(' expression ')' '{' statemenst '}'
        # ('else' '{' statements '}')? ;;;
        # ENTRY: Tokenizer positioned on 'if'
        # EXIT: Tokenizer positioned after '}'
        self.writeXML('<ifStatement>\n')
        self.indentation += 1

        # if
        self.writeXML('if', 'KEYWORD')
        # (
        self.nextToken()
        self.expect('SYMBOL', '(')
        self.writeXML('(', 'SYMBOL')
        # expression
        self.nextToken()
        self.CompileExpression()
        # )
        self.expect('SYMBOL', ')')
        self.writeXML(')', 'SYMBOL')
        # {
        self.nextToken()
        self.expect('SYMBOL', '{')
        self.writeXML('{', 'SYMBOL')
        # statementList
        self.nextToken()
        self.CompileStatementList()
        # }
        self.expect('SYMBOL', '}')
        self.writeXML('}', 'SYMBOL')
        # else
        self.nextToken()
        if self.t.tokenType() == 'KEYWORD' and self.t.keyword() == 'else':
            self.writeXML('else', 'KEYWORD')
            # {
            self.nextToken()
            self.expect('SYMBOL', '{')
            self.writeXML('{', 'SYMBOL')
            # statementList
            self.nextToken()
            self.CompileStatementList()
            # }
            self.expect('SYMBOL', '}')
            self.writeXML('}', 'SYMBOL')
            self.nextToken()

        # /IfStatement
        self.indentation -= 1
        self.writeXML('</ifStatement>\n')

    def CompileExpression(self):
        opList = ['+', '-', '*', '/', '&', '|', '<', '>', '=']

        # compile expression
        # ;;; term (op term)* ;;;
        # ENTRY: Tokenizer positioned on term
        # EXIT: Tokenizer positioned after term
        self.writeXML('<expression>\n')
        self.indentation += 1

        # term
        self.CompileTerm()
        # (op term)*
        while True:
            if self.t.tokenType() == 'SYMBOL' and self.t.symbol() in opList:
                self.writeXML(self.t.symbol(), 'SYMBOL')
                self.nextToken()
                self.CompileTerm()
            else:
                break

        # /expression
        self.indentation -= 1
        self.writeXML('</expression>\n')

    def CompileTerm(self):
        unaryOp = ('-', '~')
        KeywordConstant = ('true', 'false', 'null', 'this')

        # compile term
        # ;;; integerConstant|stringConstant|keywordConstant|
        # varName|varName '[' expression ']'|subroutineCall|
        # '(' expression ')'|unaryOp term ;;;
        # ENTRY: Tokenizer positioned on term
        # EXIT: Tokenizer positioned after term
        self.writeXML('<term>\n')
        self.indentation += 1

        tokenT = self.t.tokenType()
        if tokenT == 'INT_CONST':
            self.writeXML('<integerConstant> ' + str(self.t.intVal()) +
                          ' </integerConstant>\n')
            self.nextToken()
        elif tokenT == 'STRING_CONST':
            self.writeXML('<stringConstant> ' + self.t.stringVal() +
                          ' </stringConstant>\n')
            self.nextToken()
        elif tokenT == 'KEYWORD':
            self.expect('KEYWORD', KeywordConstant)
            self.writeXML(self.t.keyword(), 'KEYWORD')
            self.nextToken()
        elif tokenT == 'SYMBOL':
            # '(' expression ')'
            if self.t.symbol() == '(':
                self.writeXML('(', 'SYMBOL')
                self.nextToken()
                self.CompileExpression()
                self.expect('SYMBOL', ')')
                self.writeXML(')', 'SYMBOL')
                self.nextToken()
            else:
                # unaryOp term
                self.expect('SYMBOL', unaryOp)
                self.writeXML(self.t.symbol(), 'SYMBOL')
                self.nextToken()
                self.CompileTerm()
        else:
            self.expect('IDENTIFIER')
            self.writeXML(self.t.identifier(), 'IDENTIFIER')
            self.nextToken()
            if self.t.tokenType() == 'SYMBOL' and self.t.symbol() == '[':
                self.writeXML('[', 'SYMBOL')
                self.nextToken()
                self.CompileExpression()
                self.expect('SYMBOL', ']')
                self.writeXML(']', 'SYMBOL')
                self.nextToken()
            elif self.t.tokenType() == 'SYMBOL' and self.t.symbol() == '.':
                self.writeXML('.', 'SYMBOL')
                self.nextToken()
                self.expect('IDENTIFIER')
                self.writeXML(self.t.identifier(), 'IDENTIFIER')
                self.nextToken()
                self.CompileExpressionListBlock()
                self.nextToken()
            elif self.t.tokenType() == 'SYMBOL' and self.t.symbol() == '(':
                self.CompileExpressionListBlock()
                self.nextToken()

        # /term
        self.indentation -= 1
        self.writeXML('</term>\n')

    def CompileExpressionList(self):
        # compile expressionList
        # ;;; (expression(',' expression)*)? ;;;
        # ENTRY: Tokenizer positioned on before expression
        # EXIT: Tokenizer positioned after expression
        self.writeXML('<expressionList>\n')
        self.indentation += 1

        # expression(, expression)*
        self.nextToken()
        if not (self.t.tokenType() == 'SYMBOL' and self.t.symbol() == ')'):
            self.CompileExpression()
            while True:
                if self.t.tokenType() == 'SYMBOL' and self.t.symbol() == ',':
                    self.writeXML(',', 'SYMBOL')
                    self.nextToken()
                    self.CompileExpression()
                else:
                    break

        # /expressionList
        self.indentation -= 1
        self.writeXML('</expressionList>\n')

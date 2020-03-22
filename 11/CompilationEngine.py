def wrongE(expect, got):
    raise SyntaxError("expect " + expect + " but got " + got)


class CompilationEngine:
    def __init__(self, tokenizer, filePath, SymbolTable, VMWriter):
        self.wXML = True
        if self.wXML:
            self.XMLF = open(filePath.rstrip(".jack") + '.xml', 'w')
        self.symbolTable = SymbolTable
        self.tokenizer = tokenizer
        self.vmwriter = VMWriter
        self.compileVarInit()

    def compileVarInit(self):
        # restore indentation for writeXML
        self.indentation = 0

        # restore className
        self.className = ''

        # restore segments for writeFunction
        self.functionType = ''
        self.functionName = ''
        self.functionParanum = 0

        # label count for while and if
        self.whileNo = 0
        self.ifNo = 0

    def nextToken(self):
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
        else:
            raise SyntaxError("nullError")

    def expect(self, expectType, specifics=(True, )):
        if not self.tokenizer.tokenType() == expectType:
            wrongE(str(specifics), self.tokenizer.tokenType())
        if expectType == 'SYMBOL':
            spe = self.tokenizer.symbol()
        elif expectType == 'KEYWORD':
            spe = self.tokenizer.keyword()
        elif expectType == 'IDENTIFIER':
            return self.tokenizer.identifier()
        if spe in specifics:
            return spe

        wrongE(str(specifics), spe)

    def writeXML(self, s, writeType='other'):
        if not self.wXML:
            return

        for i in range(self.indentation):
            self.XMLF.write('  ')

        if writeType == 'IDENTIFIER':
            if not self.symbolTable.KindOf(s) == 'none':
                self.XMLF.write('<identifier> name=' + s + ' kind=' +
                                self.symbolTable.KindOf(s) + ' type=' +
                                self.symbolTable.TypeOf(s) + ' index=' +
                                str(self.symbolTable.IndexOf(s)) +
                                ' </identifier>\n')
            else:
                self.XMLF.write('<identifier> name=' + s +
                                '(unrecorded) </identifier>\n')
        elif writeType == 'SYMBOL':
            if s == '<':
                s = '&lt;'
            elif s == '>':
                s = '&gt;'
            elif s == '&':
                s = '&amp;'
            self.XMLF.write('<symbol> ' + s + ' </symbol>\n')
        elif writeType == 'KEYWORD':
            self.XMLF.write('<keyword> ' + s + ' </keyword>\n')
        else:
            self.XMLF.write(s)

    def writeFunctionSupport(self, val, ty):
        if ty == 'functionType':
            self.functionType = val
        elif ty == 'functionName':
            self.functionName = self.className + '.' + val
        elif ty == 'functionLocalnum':
            if self.functionType == 'constructor':
                self.vmwriter.writeFunction(self.functionName, str(val))
                self.vmwriter.writePush('constant',
                                        self.symbolTable.VarCount('field'))
                self.vmwriter.writeCall('Memory.alloc', 1)
                self.vmwriter.writePop('pointer', 0)
            elif self.functionType == 'function':
                self.vmwriter.writeFunction(self.functionName, str(val))
            elif self.functionType == 'method':
                self.vmwriter.writeFunction(self.functionName, str(val))
                self.vmwriter.writePush('argument', 0)
                self.vmwriter.writePop('pointer', 0)
            else:
                wrongE('method|constructor|function', self.functionType)
        else:
            wrongE('functionType|functionName|functionParanum', ty)

    def CompiletypeVar(self):
        # compile var
        # ;;; type varName ( ',' varName)* ';' ;;;
        # ENTRY: Tokenizer positioned brfore type
        # EXIT: Tokenizer positioned on ';'

        # type
        self.nextToken()
        if self.tokenizer.tokenType() == 'IDENTIFIER':
            self.symbolTable.preDefine(self.tokenizer.identifier(), 'type')
            self.writeXML(self.tokenizer.identifier(), 'IDENTIFIER')
        else:
            self.expect('KEYWORD', ('int', 'char', 'boolean'))
            self.symbolTable.preDefine(self.tokenizer.keyword(), 'type')
            self.writeXML(self.tokenizer.keyword(), 'KEYWORD')

        # varName
        self.nextToken()
        self.expect('IDENTIFIER')
        varName = self.tokenizer.identifier()
        self.symbolTable.preDefine(varName, 'name')
        self.writeXML(varName, 'IDENTIFIER')
        varCount = 1
        # initialize the variable
        if self.symbolTable.KindOf(varName) == 'static':
            self.vmwriter.writePush('constant', 0)
            self.vmwriter.writePop(self.symbolTable.KindOf(varName),
                                   self.symbolTable.IndexOf(varName))

        # (',' varName)*
        while True:
            self.nextToken()
            if self.tokenizer.tokenType(
            ) == 'SYMBOL' and self.tokenizer.symbol() == ';':
                self.writeXML(';', 'SYMBOL')
                break
            else:
                # ','
                self.expect('SYMBOL', ',')
                self.writeXML(',', 'SYMBOL')

                # varName
                self.nextToken()
                self.expect('IDENTIFIER')
                varName = self.tokenizer.identifier()
                self.symbolTable.preDefine(varName, 'name')
                self.writeXML(varName, 'IDENTIFIER')
                varCount += 1
                # initialize the variable
                if not self.symbolTable.KindOf(varName) == 'var':
                    self.vmwriter.writePush('constant', 0)
                    self.vmwriter.writePop(self.symbolTable.KindOf(varName),
                                           self.symbolTable.IndexOf(varName))

        return varCount

    def CompileExpressionListBlock(self):
        # Compile expressionList block
        # ;;; '(' expressionList ')' ;;;
        # ENTRY: Tokenizer positioned on '('
        # EXIT: Tokenizer positioned on ')'
        self.expect('SYMBOL', '(')
        self.writeXML('(', 'SYMBOL')
        expressionCount = self.CompileExpressionList()
        self.expect('SYMBOL', ')')
        self.writeXML(')', 'SYMBOL')
        return expressionCount

    def Compile(self):
        self.nextToken()
        self.CompileClass()
        self.XMLF.close()

    def CompileClass(self):
        # compile class
        # ;;; 'class' className '{' classVarDec* subroutineDec* '}' ;;;
        # ENTRY: Tokenizer positioned on 'class'
        # EXIT: Tokenizer positioned on '}'

        self.expect('KEYWORD', 'class')
        self.writeXML('<class>\n')
        self.indentation += 1
        # 'class'
        self.writeXML(self.tokenizer.keyword(), 'KEYWORD')
        # identifier
        self.nextToken()
        self.expect('IDENTIFIER')
        self.className = self.tokenizer.identifier()
        self.writeXML(self.tokenizer.identifier(), 'IDENTIFIER')
        # '{'
        self.nextToken()
        self.expect('SYMBOL', '{')
        self.writeXML('{', 'SYMBOL')
        # classVarDec* and subroutine*
        while True:
            self.nextToken()
            if self.tokenizer.tokenType(
            ) == 'SYMBOL' and self.tokenizer.symbol() == '}':
                break
            elif self.tokenizer.tokenType() == 'KEYWORD':
                keyword = self.tokenizer.keyword()
                if keyword in ('static', 'field'):
                    self.CompileClassVarDec()
                    continue
                elif keyword in ('constructor', 'function', 'method'):
                    self.CompileSubroutine()
                    continue
            wrongE('classVarDec* and subroutine*', self.tokenizer.tokenType())
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
        self.symbolTable.preDefine(self.tokenizer.keyword(), 'kind')
        self.writeXML(self.tokenizer.keyword(), 'KEYWORD')
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
        self.symbolTable.startSubroutine()

        # construcor | function | method
        self.writeXML(self.tokenizer.keyword(), 'KEYWORD')
        self.writeFunctionSupport(self.tokenizer.keyword(), 'functionType')
        if self.tokenizer.keyword() == 'method':
            self.symbolTable.Define('this', self.className, 'arg')
        # type
        self.nextToken()
        if self.tokenizer.tokenType() == 'IDENTIFIER':
            self.writeXML(self.tokenizer.identifier(), 'IDENTIFIER')
        else:
            self.expect('KEYWORD', ('int', 'char', 'boolean', 'void'))
            self.writeXML(self.tokenizer.keyword(), 'KEYWORD')
        # subroutineName
        self.nextToken()
        self.expect('IDENTIFIER')
        self.writeXML(self.tokenizer.identifier(), 'IDENTIFIER')
        self.writeFunctionSupport(self.tokenizer.identifier(), 'functionName')
        # '('
        self.nextToken()
        self.expect('SYMBOL', '(')
        self.writeXML(self.tokenizer.symbol(), 'SYMBOL')
        # parameterList
        self.CompileParameterList()
        # ')'
        self.expect('SYMBOL', ')')
        self.writeXML(self.tokenizer.symbol(), 'SYMBOL')

        # subroutineBody
        self.writeXML('<subroutineBody>\n')
        self.indentation += 1

        # {
        self.nextToken()
        self.expect('SYMBOL', '{')
        self.writeXML(self.tokenizer.symbol(), 'SYMBOL')
        # varDec*
        localCount = 0
        while True:
            self.nextToken()
            if self.tokenizer.tokenType(
            ) == 'KEYWORD' and self.tokenizer.keyword() == 'var':
                localCount += self.CompileVarDec()
            else:
                break
        self.writeFunctionSupport(localCount, 'functionLocalnum')
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
        self.symbolTable.preDefine('arg', 'kind')

        # type
        while True:
            self.nextToken()
            if self.tokenizer.tokenType(
            ) == 'SYMBOL' and self.tokenizer.symbol() == ')':
                break
            elif self.tokenizer.tokenType(
            ) == 'SYMBOL' and self.tokenizer.symbol() == ',':
                # ','
                self.writeXML(',', 'SYMBOL')
                # type
                self.nextToken()
                if self.tokenizer.tokenType() == 'IDENTIFIER':
                    self.symbolTable.preDefine(self.tokenizer.identifier(),
                                               'type')
                    self.writeXML(self.tokenizer.identifier(), 'IDENTIFIER')
                else:
                    self.expect('KEYWORD', ('int', 'char', 'boolean'))
                    self.symbolTable.preDefine(self.tokenizer.keyword(),
                                               'type')
                    self.writeXML(self.tokenizer.keyword(), 'KEYWORD')
                # varName
                self.nextToken()
                self.expect('IDENTIFIER')
                varName = self.tokenizer.identifier()
                self.symbolTable.preDefine(varName, 'name')
                self.writeXML(varName, 'IDENTIFIER')
            else:
                # type
                if self.tokenizer.tokenType() == 'IDENTIFIER':
                    self.symbolTable.preDefine(self.tokenizer.identifier(),
                                               'type')
                    self.writeXML(self.tokenizer.identifier(), 'IDENTIFIER')
                else:
                    self.expect('KEYWORD', ('int', 'char', 'boolean'))
                    self.symbolTable.preDefine(self.tokenizer.keyword(),
                                               'type')
                    self.writeXML(self.tokenizer.keyword(), 'KEYWORD')
                # varName
                self.nextToken()
                self.expect('IDENTIFIER')
                self.symbolTable.preDefine(self.tokenizer.identifier(), 'name')
                self.writeXML(self.tokenizer.identifier(), 'IDENTIFIER')

        self.indentation -= 1
        self.writeXML('</parameterList>\n')

    def CompileVarDec(self):
        # compile VarDec
        # ;;; 'var' type varName (',' varName)* ';' ;;;
        # ENTRY: Tokenizer positioned on 'var'
        # EXIT: Tokenizer positioned on ';'
        self.writeXML('<varDec>\n')
        self.indentation += 1
        self.symbolTable.preDefine('var', 'kind')

        self.writeXML('var', 'KEYWORD')
        varCount = self.CompiletypeVar()

        # /varDec
        self.indentation -= 1
        self.writeXML('</varDec>\n')
        return varCount

    def CompileStatementList(self):
        # compile statementList
        # ;;; statement* ;;;
        # ENTRY: Tokenizer positioned on statement
        # EXIT: Tokenizer positioned after statement
        self.writeXML('<statementList>\n')
        self.indentation += 1

        while self.tokenizer.tokenType() == 'KEYWORD':
            keyword = self.tokenizer.keyword()
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
        Name = self.tokenizer.identifier()
        self.writeXML(Name, 'IDENTIFIER')
        self.nextToken()
        if self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol(
        ) == '.':
            # '.'
            self.writeXML('.', 'SYMBOL')

            # subroutineName
            self.nextToken()
            self.expect('IDENTIFIER')
            subName = self.tokenizer.identifier()
            self.writeXML(subName, 'IDENTIFIER')
            # whether Name is one of the variableNames
            if self.symbolTable.KindOf(Name) == 'none':
                Name = Name + '.' + subName
                self.nextToken()
                expressionCount = self.CompileExpressionListBlock()
            else:
                self.vmwriter.writePush(self.symbolTable.KindOf(Name),
                                        self.symbolTable.IndexOf(Name))
                Name = self.symbolTable.TypeOf(Name) + '.' + subName
                self.nextToken()
                expressionCount = self.CompileExpressionListBlock() + 1
        else:
            self.vmwriter.writePush('pointer', 0)
            Name = self.className + '.' + Name
            expressionCount = self.CompileExpressionListBlock() + 1

        self.vmwriter.writeCall(Name, expressionCount)
        self.vmwriter.writePop('temp', 0)

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
        ifArray = False

        # 'let'
        self.writeXML('let', 'KEYWORD')
        # varName
        self.nextToken()
        self.expect('IDENTIFIER')
        varName = self.tokenizer.identifier()
        self.writeXML(varName, 'IDENTIFIER')

        # '[' ?
        self.nextToken()
        if self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol(
        ) == '[':
            # Push varName
            self.vmwriter.writePush(self.symbolTable.KindOf(varName),
                                    self.symbolTable.IndexOf(varName))
            self.writeXML('[', 'SYMBOL')
            # expression
            self.nextToken()
            self.CompileExpression()
            # ']'
            self.expect('SYMBOL', ']')
            self.writeXML(']', 'SYMBOL')
            self.nextToken()
            # Add varName and k in [k]
            self.vmwriter.writeArithmetic('add')
            ifArray = True
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
        # assignment in VMFile
        if ifArray:
            self.vmwriter.writePop('temp', 0)
            self.vmwriter.writePop('pointer', 1)
            self.vmwriter.writePush('temp', 0)
            self.vmwriter.writePop('that', 0)
        else:
            self.vmwriter.writePop(self.symbolTable.KindOf(varName),
                                   self.symbolTable.IndexOf(varName))

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
        # save currunt while label count
        whileNo = self.whileNo
        # while label increment
        self.whileNo += 1

        self.vmwriter.writeLabel('WHILE_A' + str(whileNo))
        # while
        self.writeXML('while', 'KEYWORD')
        # (
        self.nextToken()
        self.expect('SYMBOL', '(')
        self.writeXML('(', 'SYMBOL')
        # expression
        self.nextToken()
        self.CompileExpression()
        self.vmwriter.writeArithmetic('not')
        self.vmwriter.writeIf('WHILE_B' + str(whileNo))
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
        self.vmwriter.writeGoto('WHILE_A' + str(whileNo))
        self.vmwriter.writeLabel('WHILE_B' + str(whileNo))
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
        if self.tokenizer.tokenType() == 'SYMBOL' and self.tokenizer.symbol(
        ) == ';':
            self.writeXML(';', 'SYMBOL')
            self.vmwriter.writePush('constant', 0)
        else:
            self.CompileExpression()
            self.expect('SYMBOL', ';')
            self.writeXML(';', 'SYMBOL')
        self.vmwriter.writeReturn()
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
        # save if label count
        ifNo = self.ifNo
        # if label increment
        self.ifNo += 1

        # if
        self.writeXML('if', 'KEYWORD')
        # (
        self.nextToken()
        self.expect('SYMBOL', '(')
        self.writeXML('(', 'SYMBOL')
        # expression
        self.nextToken()
        self.CompileExpression()
        self.vmwriter.writeArithmetic('not')
        self.vmwriter.writeIf('IF_A' + str(ifNo))
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
        self.vmwriter.writeGoto('IF_B' + str(ifNo))
        # }
        self.expect('SYMBOL', '}')
        self.writeXML('}', 'SYMBOL')
        # else
        self.nextToken()
        self.vmwriter.writeLabel('IF_A' + str(ifNo))
        if self.tokenizer.tokenType() == 'KEYWORD' and self.tokenizer.keyword(
        ) == 'else':
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

        self.vmwriter.writeLabel('IF_B' + str(ifNo))

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
            if self.tokenizer.tokenType(
            ) == 'SYMBOL' and self.tokenizer.symbol() in opList:
                op = self.tokenizer.symbol()
                self.writeXML(op, 'SYMBOL')
                self.nextToken()
                self.CompileTerm()
                if op == '+':
                    self.vmwriter.writeArithmetic('add')
                elif op == '-':
                    self.vmwriter.writeArithmetic('sub')
                elif op == '&':
                    self.vmwriter.writeArithmetic('and')
                elif op == '|':
                    self.vmwriter.writeArithmetic('or')
                elif op == '<':
                    self.vmwriter.writeArithmetic('lt')
                elif op == '>':
                    self.vmwriter.writeArithmetic('gt')
                elif op == '=':
                    self.vmwriter.writeArithmetic('eq')
                elif op == '*':
                    self.vmwriter.writeCall('Math.multiply', '2')
                elif op == '/':
                    self.vmwriter.writeCall('Math.divide', '2')
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

        tokenT = self.tokenizer.tokenType()
        if tokenT == 'INT_CONST':
            intVal = str(self.tokenizer.intVal())
            self.writeXML('<integerConstant> ' + intVal +
                          ' </integerConstant>\n')
            self.vmwriter.writePush('constant', intVal)
            self.nextToken()
        elif tokenT == 'STRING_CONST':
            s = self.tokenizer.stringVal()
            self.writeXML('<stringConstant> ' + s + ' </stringConstant>\n')
            self.vmwriter.writePush('constant', len(s))
            self.vmwriter.writeCall('String.new', '1')
            while s:
                self.vmwriter.writePush('constant', ord(s[0]))
                self.vmwriter.writeCall('String.appendChar', '2')
                s = s[1:]
            self.nextToken()
        elif tokenT == 'KEYWORD':
            self.expect('KEYWORD', KeywordConstant)
            keyword = self.tokenizer.keyword()
            self.writeXML(keyword, 'KEYWORD')
            if keyword == 'true':
                self.vmwriter.writePush('constant', 1)
                self.vmwriter.writeArithmetic('neg')
            elif keyword == 'false':
                self.vmwriter.writePush('constant', 0)
            elif keyword == 'null':
                self.vmwriter.writePush('constant', 0)
            elif keyword == 'this':
                self.vmwriter.writePush('pointer', 0)
            else:
                wrongE('true|false|null|this', keyword)
            self.nextToken()
        elif tokenT == 'SYMBOL':
            # '(' expression ')'
            if self.tokenizer.symbol() == '(':
                self.writeXML('(', 'SYMBOL')
                self.nextToken()
                self.CompileExpression()
                self.expect('SYMBOL', ')')
                self.writeXML(')', 'SYMBOL')
                self.nextToken()
            else:
                # unaryOp term
                self.expect('SYMBOL', unaryOp)
                unaryOp = self.tokenizer.symbol()
                self.writeXML(unaryOp, 'SYMBOL')
                self.nextToken()
                self.CompileTerm()
                if unaryOp == '-':
                    self.vmwriter.writeArithmetic('neg')
                else:
                    self.vmwriter.writeArithmetic('not')
        else:
            self.expect('IDENTIFIER')
            Name = self.tokenizer.identifier()
            self.writeXML(Name, 'IDENTIFIER')
            self.nextToken()
            if self.tokenizer.tokenType(
            ) == 'SYMBOL' and self.tokenizer.symbol() == '[':
                self.vmwriter.writePush(self.symbolTable.KindOf(Name),
                                        self.symbolTable.IndexOf(Name))
                self.writeXML('[', 'SYMBOL')
                self.nextToken()
                self.CompileExpression()
                self.vmwriter.writeArithmetic('add')
                self.vmwriter.writePop('pointer', 1)
                self.vmwriter.writePush('that', 0)
                self.expect('SYMBOL', ']')
                self.writeXML(']', 'SYMBOL')
                self.nextToken()
            elif self.tokenizer.tokenType(
            ) == 'SYMBOL' and self.tokenizer.symbol() == '.':
                self.writeXML('.', 'SYMBOL')

                self.nextToken()
                self.expect('IDENTIFIER')
                subName = self.tokenizer.identifier()
                self.writeXML(subName, 'IDENTIFIER')
                # whether Name is one of the variableNames
                if self.symbolTable.KindOf(Name) == 'none':
                    Name = Name + '.' + subName
                    self.nextToken()
                    expressionCount = self.CompileExpressionListBlock()
                else:
                    self.vmwriter.writePush(self.symbolTable.KindOf(Name),
                                            self.symbolTable.IndexOf(Name))
                    Name = self.symbolTable.TypeOf(Name) + '.' + subName
                    self.nextToken()
                    expressionCount = self.CompileExpressionListBlock() + 1
                self.vmwriter.writeCall(Name, expressionCount)
                self.nextToken()
            elif self.tokenizer.tokenType(
            ) == 'SYMBOL' and self.tokenizer.symbol() == '(':
                self.vmwriter.writePush('pointer', 0)
                Name = self.className + '.' + Name
                expressionCount = self.CompileExpressionListBlock() + 1
                self.vmwriter.writeCall(Name, expressionCount)
                self.nextToken()
            else:
                self.vmwriter.writePush(self.symbolTable.KindOf(Name),
                                        self.symbolTable.IndexOf(Name))

        # /term
        self.indentation -= 1
        self.writeXML('</term>\n')

    def CompileExpressionList(self):
        # compile expressionList
        # ;;; (expression(',' expression)*)? ;;;
        # ENTRY: Tokenizer positioned on before expression
        # EXIT: Tokenizer positioned after expression
        expressionCount = 0
        self.writeXML('<expressionList>\n')
        self.indentation += 1

        # expression(, expression)*
        self.nextToken()
        if not (self.tokenizer.tokenType() == 'SYMBOL'
                and self.tokenizer.symbol() == ')'):
            expressionCount += 1
            self.CompileExpression()

            while True:
                if self.tokenizer.tokenType(
                ) == 'SYMBOL' and self.tokenizer.symbol() == ',':
                    self.writeXML(',', 'SYMBOL')

                    expressionCount += 1
                    self.nextToken()
                    self.CompileExpression()
                else:
                    break

        # /expressionList
        self.indentation -= 1
        self.writeXML('</expressionList>\n')
        return expressionCount

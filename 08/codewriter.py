functionCallCount, eqcounter, ltcounter, gtcounter = 0, 0, 0, 0
currentFunctionName = 'null'
fname = ''


def openfile():
    global outputName, f
    f = open(outputName, 'w')


def setFileName1(name):
    global outputName, fname
    outputName = name.rstrip('.vm') + '.asm'
    fname = outputName[outputName.rfind('/') + 1:].rstrip('.asm')


def setFileName2(name):
    global outputName, fname
    outputName = name + '/' + name[name.rfind('/') + 1:] + '.asm'


def writeArithmetic(command):
    global f, eqcounter, ltcounter, gtcounter
    if command == 'add':
        f.write('@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nM=D+M\n')
    elif command == 'sub':
        f.write('@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nM=M-D\n')
    elif command == 'neg':
        f.write('@SP\nA=M-1\nM=-M\n')
    elif command == 'eq':
        eqc = str(eqcounter)
        f.write('@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nD=M-D\n@EQ' + eqc +
                '\nD;JEQ\n@SP\nA=M\nM=0\n@EQ' + eqc + 'A\n0;JEQ\n(EQ' + eqc +
                ')\n@SP\nA=M\nM=-1\n(EQ' + eqc + 'A)\n@SP\nM=M+1\n')
        eqcounter += 1
    elif command == 'gt':
        gtc = str(gtcounter)
        f.write('@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nD=M-D\n@GT' + gtc +
                '\nD;JGT\n@SP\nA=M\nM=0\n@GT' + gtc + 'A\n0;JEQ\n(GT' + gtc +
                ')\n@SP\nA=M\nM=-1\n(GT' + gtc + 'A)\n@SP\nM=M+1\n')
        gtcounter += 1
    elif command == 'lt':
        ltc = str(ltcounter)
        f.write('@SP\nAM=M-1\nD=M\n@SP\nAM=M-1\nD=M-D\n@LT' + ltc +
                '\nD;JLT\n@SP\nA=M\nM=0\n@LT' + ltc + 'A\n0;JEQ\n(LT' + ltc +
                ')\n@SP\nA=M\nM=-1\n(LT' + ltc + 'A)\n@SP\nM=M+1\n')
        ltcounter += 1
    elif command == 'and':
        f.write('@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nM=D&M\n')
    elif command == 'or':
        f.write('@SP\nAM=M-1\nD=M\n@SP\nA=M-1\nM=D|M\n')
    elif command == 'not':
        f.write('@SP\nA=M-1\nM=!M\n')


def writePushPop(command, segment, index):
    global f, fname
    if command == 'C_PUSH':
        if segment == 'constant':
            f.write('@' + str(index) + '\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
        elif segment == 'local':
            f.write('@LCL\nD=M\n@' + str(index) +
                    '\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
        elif segment == 'argument':
            f.write('@ARG\nD=M\n@' + str(index) +
                    '\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
        elif segment == 'this':
            f.write('@THIS\nD=M\n@' + str(index) +
                    '\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
        elif segment == 'that':
            f.write('@THAT\nD=M\n@' + str(index) +
                    '\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
        elif segment == 'pointer':
            if index == 0 or index == 1:
                f.write('@' + str(3 + index) +
                        '\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
            else:
                raise ValueError('arg2 for pointer in C_PUSH is invalid: %s'
                                 % index)
        elif segment == 'temp':
            if index in range(8):
                f.write('@' + str(5 + index) +
                        '\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
            else:
                raise ValueError('arg2 for temp in C_PUSH is invalid: %s'
                                 % index)
        elif segment == 'static':
            f.write('@' + fname + '.' + str(index) +
                    '\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
    elif command == 'C_POP':
        if segment == 'constant':
            raise ValueError('C_POP for constant is invalid: %s' % segment)
        elif segment == 'local':
            f.write('@LCL\nD=M\n@' + str(index) +
                    '\nD=A+D\n@t\nM=D\n@SP\nAM=M-1\nD=M\n@t\nA=M\nM=D\n')
        elif segment == 'argument':
            f.write('@ARG\nD=M\n@' + str(index) +
                    '\nD=A+D\n@t\nM=D\n@SP\nAM=M-1\nD=M\n@t\nA=M\nM=D\n')
        elif segment == 'this':
            f.write('@THIS\nD=M\n@' + str(index) +
                    '\nD=A+D\n@t\nM=D\n@SP\nAM=M-1\nD=M\n@t\nA=M\nM=D\n')
        elif segment == 'that':
            f.write('@THAT\nD=M\n@' + str(index) +
                    '\nD=A+D\n@t\nM=D\n@SP\nAM=M-1\nD=M\n@t\nA=M\nM=D\n')
        elif segment == 'pointer':
            if index == 0 or index == 1:
                f.write('@SP\nAM=M-1\nD=M\n@' + str(3 + index) + '\nM=D\n')
            else:
                raise ValueError('arg2 for pointer in C_POP is invalid: %s'
                                 % index)
        elif segment == 'temp':
            if index in range(8):
                f.write('@SP\nAM=M-1\nD=M\n@' + str(5 + index) + '\nM=D\n')
            else:
                raise ValueError('arg2 for temp in C_POP is invalid: %s'
                                 % index)
        elif segment == 'static':
            f.write('@SP\nAM=M-1\nD=M\n@' + fname + '.' + str(index) +
                    '\nM=D\n')


def writeInit():
    global f
    f.write('@256\nD=A\n@SP\nM=D\n')
    writeCall('Sys.init', 0)


def writeLabel(label):
    global f, currentFunctionName
    f.write('(' + currentFunctionName[-1] + '$' + label + ')\n')


def writeGoto(label):
    global f, currentFunctionName
    f.write('@' + currentFunctionName[-1] + '$' + label + '\n0;JMP\n')


def writeIf(label):
    global f, currentFunctionName
    f.write('@SP\nAM=M-1\nD=M\n@' + currentFunctionName[-1] +
            '$' + label + '\nD;JNE\n')


def writeCall(functionName, numArgs):
    global f, functionCallCount
    f.write('@returnAddress' + str(functionCallCount) +
            '\nD=A\n@SP\nA=M\nM=D\n@LCL\nD=M\n@SP\nAM=M+1\nM=D\n@ARG\nD=M\n@SP'
            '\nAM=M+1\nM=D\n@THIS\nD=M\n@SP\nAM=M+1\nM=D\n@THAT\nD=M\n@SP\n'
            'AM=M+1\nM=D\n@SP\nM=M+1\n@5\nD=A\n@' + str(numArgs) + '\nD=D+A\n'
            '@SP\nD=M-D\n@ARG\nM=D\n@SP\nD=M\n@LCL\nM=D\n@' + functionName +
            '\n0;JMP\n(returnAddress' + str(functionCallCount) + ')\n')
    functionCallCount += 1


def writeReturn():
    global f
    f.write('@LCL\nD=M\n@FRAME\nM=D\n@5\nD=D-A\nA=D\nD=M\n@RET\nM=D\n@SP\n'
            'A=M-1\nD=M\n@ARG\nA=M\nM=D\n@ARG\nD=M+1\n@SP\nM=D\n@FRAME\n'
            'D=M-1\nA=D\nD=M\n@THAT\nM=D\n@FRAME\nD=M\n@2\nD=D-A\nA=D\nD=M\n'
            '@THIS\nM=D\n@FRAME\nD=M\n@3\nD=D-A\nA=D\nD=M\n@ARG\nM=D\n'
            '@FRAME\nD=M\n@4\nD=D-A\nA=D\nD=M\n@LCL\nM=D\n@RET\nD=M\nA=D\n'
            '0;JMP\n')


def writeFunction(functionName, numLocals):
    global f, currentFunctionName
    currentFunctionName = functionName
    s = ''
    while numLocals > 0:
        s += '@SP\nA=M\nM=0\n@SP\nM=M+1\n'
        numLocals -= 1
    f.write('(' + functionName + ')\n' + s)


def closefile():
    global f
    f.close()

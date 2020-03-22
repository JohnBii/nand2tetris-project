eqcounter, ltcounter, gtcounter = 0, 0, 0


def openfile():
    global outputName, f
    f = open(outputName, 'w')


def setFileName(name):
    global outputName
    outputName = name.rstrip('.vm') + '.asm'


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
    global f, outputName
    filename = outputName[outputName.rfind('/') + 1:].rstrip('.asm')
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
            f.write('@' + filename + '.' + str(index) +
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
            f.write('@SP\nAM=M-1\nD=M\n@' + filename + '.' + str(index) +
                    '\nM=D\n')


def closefile():
    global f
    f.close()

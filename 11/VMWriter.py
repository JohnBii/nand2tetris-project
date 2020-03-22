class VMWriter:
    def __init__(self, filename):
        self.f = open(filename.rstrip(".jack") + '.vm', 'w')

    def transfer(self, origin):
        if origin == 'field':
            return 'this'
        elif origin == 'var':
            return 'local'
        elif origin == 'arg':
            return 'argument'
        else:
            return origin

    def writePush(self, segment, index):
        self.f.write('push ' + self.transfer(segment) + ' ' + str(index) +
                     '\n')

    def writePop(self, segment, index):
        self.f.write('pop ' + self.transfer(segment) + ' ' + str(index) +
                     '\n')

    def writeArithmetic(self, command):
        self.f.write('' + command + '\n')

    def writeLabel(self, label):
        self.f.write('label ' + label + '\n')

    def writeGoto(self, label):
        self.f.write('goto ' + label + '\n')

    def writeIf(self, label):
        self.f.write('if-goto ' + label + '\n')

    def writeCall(self, name, nArgs):
        self.f.write('call ' + name + ' ' + str(nArgs) + '\n')

    def writeFunction(self, name, nArgs):
        self.f.write('function ' + name + ' ' + str(nArgs) + '\n')

    def writeReturn(self):
        self.f.write('return\n')

    def close(self):
        self.f.close()

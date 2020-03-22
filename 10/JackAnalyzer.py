import os
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine


def dealWithJack(filePath):
    token = JackTokenizer(filePath)
    f = open(filePath.rstrip(".jack") + 'A.xml', 'w')
    c = CompilationEngine(token, f)
    c.Compile()
    token.closeFile()
    f.close()


print("Please input the jack-file or jack-directory to be translated: ")
path = input()
if not os.path.isdir(path):
    dealWithJack(path)
else:
    files = os.listdir(path)
    for file in files:
        if (not (os.path.isdir(path + '/' + file)) and '.jack' in file):
            dealWithJack(path + '/' + file)

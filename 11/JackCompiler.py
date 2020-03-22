import os
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
from SymbolTable import SymbolTable
from VMWriter import VMWriter


def dealWithJack(filePath):
    tokenizer = JackTokenizer(filePath)
    vmwriter = VMWriter(filePath)
    c = CompilationEngine(tokenizer, filePath, SymbolTable(), vmwriter)
    c.Compile()
    tokenizer.closeFile()
    vmwriter.close()


print("Please input the jack-file or jack-directory to be translated: ")
path = input()
if not os.path.isdir(path):
    dealWithJack(path)
else:
    files = os.listdir(path)
    for file in files:
        if (not (os.path.isdir(path + '/' + file)) and '.jack' in file):
            dealWithJack(path + '/' + file)

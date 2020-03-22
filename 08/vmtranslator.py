import os
import codeparser
import codewriter


def dealWithFile(filepath):
    codeparser.obtainName(filepath)
    codeparser.openfile()
    while codeparser.hasMoreCommands():
        codeparser.advance()
        ty = codeparser.commandType()
        if ty == 'C_ARITHMETIC':
            codewriter.writeArithmetic(codeparser.current_command)
            # 这里潜在的bug是currentcommand可能不会动态赋值
        elif ty == 'C_PUSH' or ty == 'C_POP':
            codewriter.writePushPop(ty, codeparser.arg1(), codeparser.arg2())
        elif ty == 'C_LABEL':
            codewriter.writeLabel(codeparser.arg1())
        elif ty == 'C_GOTO':
            codewriter.writeGoto(codeparser.arg1())
        elif ty == 'C_IF':
            codewriter.writeIf(codeparser.arg1())
        elif ty == 'C_FUNCTION':
            codewriter.writeFunction(codeparser.arg1(), codeparser.arg2())
        elif ty == 'C_RETURN':
            codewriter.writeReturn()
        elif ty == 'C_CALL':
            codewriter.writeCall(codeparser.arg1(), codeparser.arg2())
    codeparser.closefile()


print("Please input the vm-file or vm-directory to be translated: ")
path = input()
if not os.path.isdir(path):
    codewriter.setFileName1(path)
    codewriter.openfile()
    codewriter.writeInit()
    dealWithFile(path)
    codewriter.closefile()
else:
    files = os.listdir(path)
    codewriter.setFileName2(path)
    codewriter.openfile()
    codewriter.fname = 'Sys.Init'
    codewriter.writeInit()
    for file in files:
        if not os.path.isdir(path + '/' + file) and '.vm' in file:
            codewriter.fname = file
            dealWithFile(path + '/' + file)
    codewriter.closefile()

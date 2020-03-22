import codeparser
import codewriter
print("Please input the vm-file or vm-directory to be translated: ")
name = input()
codeparser.obtainName(name)
codewriter.setFileName(name)
codeparser.openfile()
codewriter.openfile()
while codeparser.hasMoreCommands():
    codeparser.advance()
    ty = codeparser.commandType()
    if ty == 'C_ARITHMETIC':
        codewriter.writeArithmetic(codeparser.current_command)
        # 这里潜在的bug是currentcommand可能不会动态赋值
    elif ty == 'C_PUSH' or ty == 'C_POP':
        codewriter.writePushPop(ty, codeparser.arg1(), codeparser.arg2())
    elif ty == 'C_LABEL':
        pass
    elif ty == 'C_GOTO':
        pass
    elif ty == 'C_IF':
        pass
    elif ty == 'C_FUNCTION':
        pass
    elif ty == 'C_RETURN':
        pass
    elif ty == 'C_CALL':
        pass
codeparser.closefile()
codewriter.closefile()

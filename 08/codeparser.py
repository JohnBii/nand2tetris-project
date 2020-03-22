name = ''
current_command = ''
next_command = ''


def obtainName(s):
    global name
    name = s


def openfile():
    global f
    f = open(name, 'r')


def hasMoreCommands():
    global next_command, f
    next_command = f.readline()
    if not next_command:
        return False
    else:
        next_command = next_command.strip()
        if not next_command:
            return hasMoreCommands()
        elif 0 == next_command.find('/'):
            return hasMoreCommands()
        elif '/' in next_command:
            next_command = next_command[:next_command.index('/')].rstrip()
            return True
        else:
            return True


def advance():
    global current_command, next_command
    current_command = next_command


def commandType():
    global current_command
    clue = current_command[:2].lower()
    if clue == 'ad':
        return 'C_ARITHMETIC'
    elif clue == 'su':
        return 'C_ARITHMETIC'
    elif clue == 'ne':
        return 'C_ARITHMETIC'
    elif clue == 'eq':
        return 'C_ARITHMETIC'
    elif clue == 'gt':
        return 'C_ARITHMETIC'
    elif clue == 'lt':
        return 'C_ARITHMETIC'
    elif clue == 'an':
        return 'C_ARITHMETIC'
    elif clue == 'or':
        return 'C_ARITHMETIC'
    elif clue == 'no':
        return 'C_ARITHMETIC'
    elif clue == 'pu':
        return 'C_PUSH'
    elif clue == 'po':
        return 'C_POP'
    elif clue == 'la':
        return 'C_LABEL'
    elif clue == 'go':
        return 'C_GOTO'
    elif clue == 'if':
        return 'C_IF'
    elif clue == 'fu':
        return 'C_FUNCTION'
    elif clue == 're':
        return 'C_RETURN'
    elif clue == 'ca':
        return 'C_CALL'
    else:
        raise ValueError('Invalid command: %s' % current_command)


def arg1():
    global current_command
    command_type = commandType()
    if command_type == 'C_ARITHMETIC':
        s = current_command
    elif command_type == 'C_PUSH':
        s = current_command[4:].lstrip()
    elif command_type == 'C_POP':
        s = current_command[3:].lstrip()
    elif command_type == 'C_LABEL':
        s = current_command[5:].lstrip() + ' '
    elif command_type == 'C_GOTO':
        s = current_command[4:].lstrip() + ' '
    elif command_type == 'C_IF':
        s = current_command[7:].lstrip() + ' '
    elif command_type == 'C_FUNCTION':
        s = current_command[8:].lstrip()
    elif command_type == 'C_CALL':
        s = current_command[4:].lstrip()
    else:
        raise ValueError('Invalid command type that calling for arg1: %s'
                         % command_type)
    return s[:s.index(' ')]


def arg2():
    global current_command
    command_type = commandType()
    if command_type == 'C_PUSH' or command_type == 'C_POP' or \
            command_type == 'C_CALL' or command_type == 'C_FUNCTION':
        return int(current_command[current_command.rindex(' ') + 1:])
    else:
        raise ValueError("Invalid command type that calling for arg2: %s"
                         % command_type)


def closefile():
    global f
    f.close

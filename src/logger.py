from termcolor import colored, cprint

NOMSG = 0
ERROR = 1
INFO = 2
DEBUG = 3
log_file = None
level = None

def init(file_name, log_level):
    global log_file, level 
    level = log_level  
    log_file = open(file_name, 'wb', 0)

def error(text):
    if(level >= ERROR):
        log_file.write(text + '\n')
    cprint(text, 'red')

def cimportant(text):
    if(level >= ERROR):
        log_file.write(text + '\n')
    cprint(text, 'yellow')

def info(text):
    if(level >= INFO):
        log_file.write(text + '\n')
    print(text)

def cinfo(text):
    if(level >= INFO):
        log_file.write(text + '\n')
    cprint(text, 'green')

def debug(text):
    if(level >= DEBUG):
        log_file.write(text + '\n')
    cprint(text, 'yellow')

def write(text):
    log_file.write(text + '\n')

def close_log():
    log_file.close()

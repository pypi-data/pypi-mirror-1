from sys import stdout

def error(m):
    stdout.write(m + '\n')
    pass

warning = alert = error

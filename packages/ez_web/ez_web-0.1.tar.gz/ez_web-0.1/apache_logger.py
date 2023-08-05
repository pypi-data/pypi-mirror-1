from mod_python import apache

def error(m):
    apache.log_error(m, apache.APLOG_ERR)
    pass

def warning(m):
    apache.log_error(m, apache.APLOG_WARNING)
    pass

def alert(m):
    apache.log_error(m, apache.APLOG_ALERT)
    pass

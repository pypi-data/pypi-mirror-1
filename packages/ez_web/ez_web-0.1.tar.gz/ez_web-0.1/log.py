import config

if hasattr(config, 'logger'):
    logger = config.logger
    error = logger.error
    warning = logger.warning
    alert = logger.alert
else:
    error = warning = alert = lambda x: None
    pass

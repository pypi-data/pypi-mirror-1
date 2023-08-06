from logging import getLogger

logger = getLogger('setup')

def setupVarious(context):

    logger.info(dir(context))
    
    if context.readDataFile('themetweaker.themeswitcher_various.txt') is None:
        return

    # Add additional setup code here

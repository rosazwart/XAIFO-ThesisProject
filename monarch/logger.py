import logging
logging.basicConfig(level=logging.INFO, filename='monarchfetcher.log', filemode="a+", format="%(asctime)-15s %(levelname)-8s %(message)s")

def register_info(message):
    """
        Print message into console as well as given logger.
        :param current_logger: logger with configuration
        :param message: message that needs to be printed and logged
    """
    print(message)
    logging.info(message)
    
def register_error(message):
    """
        Log given error.
        :param message: message that needs to be printed and logged
    """
    print(message)
    logging.error(message)
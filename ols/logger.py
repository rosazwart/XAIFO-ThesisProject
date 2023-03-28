import logging
logging.basicConfig(level=logging.INFO, filename='ontologyanalysis.log', filemode="a+", format="%(message)s")

def register_info(message):
    """
        Print message into console as well as given logger.
        :param current_logger: logger with configuration
        :param message: message that needs to be printed and logged
    """
    print(message)
    logging.info(message)
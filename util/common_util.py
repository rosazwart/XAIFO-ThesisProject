import logging

def register_info(current_logger: logging, message):
    """
        Print message into console as well as given logger.
        :param current_logger: logger with configuration
        :param message: message that needs to be printed and logged
    """
    
    print(message)
    current_logger.info(message)
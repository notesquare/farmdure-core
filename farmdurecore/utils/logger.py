import sys
import logging


# config
log_format = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
stream_level = logging.WARNING
file_level = logging.INFO


# init
def get_logger(save_file=False):
    # stream
    stream_hdlr = logging.StreamHandler(sys.stdout)
    stream_hdlr.setFormatter(log_format)
    stream_hdlr.setLevel(stream_level)

    logger = logging.getLogger()
    logger.setLevel(stream_level)
    logger.addHandler(stream_hdlr)

    # file
    if save_file is True:
        file_hdlr = logging.handlers.TimedRotatingFileHandler(
            'log/outliner.log',
            when='midnight'
            )
        file_hdlr.setFormatter(log_format)
        file_hdlr.setLevel(file_level)
        logger.addHandler(file_hdlr)
    return logger

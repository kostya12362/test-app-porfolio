import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Redirects standard logs to loguru.
    """

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logger():
    # 1. Clear all handlers from the root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 2. Clean Scrapy loggers
    for name, log_instance in logging.root.manager.loggerDict.items():
        if isinstance(log_instance, logging.Logger):  # Let's check that it is indeed a logger
            for handler in log_instance.handlers[:]:
                log_instance.removeHandler(handler)

    # 3. Disabling the default Scrapy log settings
    # configure_logging(install_root_handler=False)

    # 4.We remove all existing handlers from loguru and add a new one
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    # 5. Redirect all standard Python logs to loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)

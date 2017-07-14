import logging.config

from . import __project_name__, settings


def init_logger() -> None:
    log_handler_name = "colored" if not settings.log_no_color else "default"
    log_level = settings.log_level
    logging.config.dictConfig(
        {
            "version": 1,
            "loggers": {
                __project_name__: {"handlers": [log_handler_name], "level": log_level},
                # TODO: Make this work
                "fastapi": {"handlers": [log_handler_name], "level": log_level},
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "colored": {
                    "formatter": "colored",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
            },
            "formatters": {
                "default": {
                    "format": "%(asctime)s.%(msecs)03d [%(levelname)-8s] %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "colored": {
                    "()": "coloredlogs.ColoredFormatter",
                    "format": "%(asctime)s.%(msecs)03d %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
        }
    )

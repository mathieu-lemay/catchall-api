import logging.config
from typing import Any

from . import Settings, __project_name__


def get_logging_config(settings: Settings) -> dict[str, Any]:
    log_level = settings.log_level.upper()

    if settings.log_no_color:
        log_format = "%(asctime)s.%(msecs)03d [%(levelname)-8s] %(name)s: %(message)s"
        log_formatter_class = "coloredlogs.BasicFormatter"
    else:
        log_format = "%(asctime)s.%(msecs)03d %(name)s: %(message)s"
        log_formatter_class = "coloredlogs.ColoredFormatter"

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            __project_name__: {"handlers": ["default"], "level": log_level},
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "formatters": {
            "default": {
                "()": log_formatter_class,
                "format": log_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
    }


def configure_loggers(settings: Settings) -> None:
    config = get_logging_config(settings)
    logging.config.dictConfig(config)

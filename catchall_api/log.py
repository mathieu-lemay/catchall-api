import logging.config

from . import Settings, __project_name__


def configure_loggers(settings: Settings) -> None:
    log_level = settings.log_level.upper()
    uvicorn_log_level = settings.uvicorn_log_level.upper()
    uvicorn_access_handlers = ["default"] if not settings.uvicorn_no_access_log else []

    if settings.log_no_color:
        log_format = "%(asctime)s.%(msecs)03d [%(levelname)-8s] %(name)s: %(message)s"
        log_formatter_class = "coloredlogs.BasicFormatter"
    else:
        log_format = "%(asctime)s.%(msecs)03d %(name)s: %(message)s"
        log_formatter_class = "coloredlogs.ColoredFormatter"

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "loggers": {
                __project_name__: {"handlers": ["default"], "level": log_level},
                "uvicorn": {"handlers": ["default"], "level": uvicorn_log_level},
                "uvicorn.access": {"handlers": uvicorn_access_handlers, "level": uvicorn_log_level},
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
    )

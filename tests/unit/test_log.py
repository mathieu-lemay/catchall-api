from typing import Any

import pytest

from catchall_api import Settings, __project_name__
from catchall_api.log import get_logging_config


@pytest.mark.parametrize(
    "log_level",
    [
        "CRITICAL",
        "critical",
        "ERROR",
        "error",
        "WARNING",
        "warning",
        "INFO",
        "info",
        "DEBUG",
        "debug",
        "NOTSET",
        "notset",
    ],
)
def test_get_log_config_sets_log_level(log_level: str) -> None:
    settings = Settings(log_level=log_level)

    log_config = get_logging_config(settings)

    log_levels = {k: v["level"] for k, v in log_config["loggers"].items()}
    assert log_levels == {__project_name__: log_level.upper()}


@pytest.mark.parametrize(
    ("no_color", "expected"),
    [
        (
            None,
            {
                "default": {
                    "()": "coloredlogs.ColoredFormatter",
                    "format": "%(asctime)s.%(msecs)03d %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
        ),
        (
            "",
            {
                "default": {
                    "()": "coloredlogs.ColoredFormatter",
                    "format": "%(asctime)s.%(msecs)03d %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
        ),
        (
            "any-non-null-non-empty-value",
            {
                "default": {
                    "()": "coloredlogs.BasicFormatter",
                    "format": (
                        "%(asctime)s.%(msecs)03d [%(levelname)-8s] %(name)s:"
                        " %(message)s"
                    ),
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
        ),
    ],
)
def test_get_log_config_uses_color_if_requested(
    no_color: str | None, expected: dict[str, Any]
) -> None:
    settings = Settings(log_no_color=no_color)

    log_config = get_logging_config(settings)

    assert log_config["formatters"] == expected

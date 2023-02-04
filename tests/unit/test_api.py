from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

from catchall_api import Settings


def test_settings(monkeypatch: MonkeyPatch) -> None:
    log_level = "log-level"
    log_no_color = "log-no-color"
    log_to_file = "1"
    log_file_directory = "/some/path"
    uvicorn_log_level = "uvicorn-log-level"
    uvicorn_no_access_log = "1"

    monkeypatch.setenv("CATCHALL_API_LOG_LEVEL", log_level)
    monkeypatch.setenv("CATCHALL_API_LOG_TO_FILE", log_to_file)
    monkeypatch.setenv("CATCHALL_API_LOG_FILE_DIRECTORY", log_file_directory)
    monkeypatch.setenv("NO_COLOR", log_no_color)
    monkeypatch.setenv("UVICORN_LOG_LEVEL", uvicorn_log_level)
    monkeypatch.setenv("UVICORN_NO_ACCESS_LOG", uvicorn_no_access_log)

    settings = Settings()

    monkeypatch.undo()

    assert settings.log_level == log_level
    assert settings.log_no_color == log_no_color
    assert settings.log_to_file is True
    assert settings.log_file_directory == Path(log_file_directory)
    assert settings.uvicorn_log_level == uvicorn_log_level
    assert settings.uvicorn_no_access_log is True


def test_settings_default_values() -> None:
    settings = Settings()

    assert settings.log_level == "INFO"
    assert settings.log_no_color is None
    assert settings.log_to_file is False
    assert settings.log_file_directory == Path("/output")
    assert settings.uvicorn_log_level == "INFO"
    assert settings.uvicorn_no_access_log is False

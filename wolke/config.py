"""
Central config: reads config.ini (path from WOLKE_CONFIG or default), env overrides for port/debug.
"""
import os
import configparser
from pathlib import Path


def _resolve_config_path() -> str:
    if os.environ.get("WOLKE_CONFIG"):
        return os.path.abspath(os.environ["WOLKE_CONFIG"])
    cwd = os.getcwd()
    # Repo root = parent of package dir (so "python -m wolke" from anywhere can find config)
    try:
        _pkg_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(_pkg_dir)
    except Exception:
        repo_root = cwd
    for candidate in [
        os.path.join(cwd, "config.ini"),
        os.path.join(repo_root, "config.ini"),
        os.path.join(os.environ.get("DATA_FOLDER", "/data"), "config.ini"),
        os.path.join(repo_root, "sample_data", "config.ini.example"),
    ]:
        if os.path.isfile(candidate):
            return os.path.abspath(candidate)
    return os.path.join(cwd, "config.ini")


class Config:
    def __init__(self, config_path: str | None = None):
        path = config_path or _resolve_config_path()
        self._path = os.path.abspath(path)
        parser = configparser.ConfigParser()
        if not os.path.isfile(self._path):
            raise FileNotFoundError(f"Config not found: {self._path}")
        parser.read(self._path)

        def _get(section: str, key: str) -> str:
            val = parser.get(section, key)
            return val.strip().strip('"').strip("'")

        # Data: resolve db path relative to config file's directory (not cwd)
        config_dir = os.path.dirname(self._path)
        raw_db = _get("data", "db_filename")
        self.db_filename = raw_db if os.path.isabs(raw_db) else os.path.join(config_dir, raw_db)
        self.db_filename = os.path.abspath(self.db_filename)
        self.table_name = _get("data", "table_name")
        self.relative_filepath_column = _get("data", "relative_filepath_column")
        self.image_base_dir = os.path.dirname(self.db_filename)

        # General (env overrides)
        self.debug = os.environ.get("WOLKE_DEBUG", "").lower() in ("1", "true", "yes")
        if not os.environ.get("WOLKE_DEBUG"):
            self.debug = parser.getboolean("general", "debug")
        port_env = os.environ.get("WOLKE_PORT")
        self.port = int(port_env) if port_env else parser.getint("general", "port")
        interval_env = os.environ.get("WOLKE_VIEWER_SYNC_INTERVAL")
        if interval_env:
            self.viewer_sync_interval_ms = int(interval_env)
        elif parser.has_option("general", "viewer_sync_interval_ms"):
            self.viewer_sync_interval_ms = parser.getint("general", "viewer_sync_interval_ms")
        else:
            self.viewer_sync_interval_ms = 1500

        # Plot
        self.plot_x = _get("plot", "x")
        self.plot_y = _get("plot", "y")
        self.plot_color = _get("plot", "color")

    @property
    def config_path(self) -> str:
        return self._path

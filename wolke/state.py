"""
App state: single source for DB data, selection, token. No globals.
"""
from __future__ import annotations

import pandas as pd
from typing import Any


class AppState:
    def __init__(
        self,
        *,
        df: pd.DataFrame,
        image_base_dir: str,
        relative_filepath_column: str,
        token: str,
    ):
        self.df = df
        self.image_base_dir = image_base_dir
        self.relative_filepath_column = relative_filepath_column
        self.token = token
        self.selected_rows: list[dict[str, Any]] = []
        self.normalize_images = False
        self.viewer_index: int | None = None
        self._last_emitted_selection_ids: tuple[int, ...] | None = None
        self._sync_table_index: int | None = None

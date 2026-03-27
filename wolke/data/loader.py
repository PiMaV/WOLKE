"""
Load DB table into DataFrame; derive categorical/numeric options for UI.

Spaltentypen werden anhand des Pandas-Dtyps entschieden:
- Numerisch: select_dtypes(include=["number"]) – INTEGER/REAL in SQLite → Histogramme, Slider, kontinuierliche Achsen.
- Kategorisch: select_dtypes(include=["object", "category"]) – TEXT in SQLite → Dropdown-Filter, diskrete Farben.
Fuer Kategorien in der UI muessen Spalten also als Text (object) vorliegen; Integer-Spalten werden immer als numerisch behandelt.
"""
import logging
import sqlite3
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class DataLoader:
    def __init__(self, db_filename: str, table_name: str, image_base_dir: str):
        self.db_filename = db_filename
        self.table_name = table_name
        self.image_base_dir = image_base_dir

    def load_data(
        self,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]], pd.DataFrame]:
        logger.info("Loading data from %s...", self.db_filename)
        with sqlite3.connect(self.db_filename) as conn:
            df = pd.read_sql(f"SELECT * FROM {self.table_name}", conn)
        logger.info("Data loaded from %s.", self.db_filename)
        if "id" not in df.columns:
            df.insert(0, "id", range(len(df)))
            logger.info("Added missing 'id' column for plot selection.")

        cat_cols = df.select_dtypes(include=["object", "category"]).columns
        df[cat_cols] = df[cat_cols].apply(lambda x: x.astype("category"))
        num_cols = df.select_dtypes(include=["number"]).columns

        all_categorical = sorted(
            [{"label": c, "value": c} for c in cat_cols],
            key=lambda x: x["label"],
        )
        all_numeric = sorted(
            [{"label": c, "value": c} for c in num_cols],
            key=lambda x: x["label"],
        )
        return all_categorical, all_numeric, df

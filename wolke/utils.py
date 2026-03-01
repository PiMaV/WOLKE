"""Shared helpers: logging, token, image normalization, histogram, sort_categories, image load."""
import hashlib
import logging
import uuid
from pathlib import Path
from typing import Any

import numpy as np
import plotly.express as px
import pandas as pd

logger = logging.getLogger(__name__)


def prinfo(msg: str, *args: Any, **kwargs: Any) -> None:
    logger.info(msg, *args, **kwargs)


def prdebug(msg: str, *args: Any, **kwargs: Any) -> None:
    logger.debug(msg, *args, **kwargs)


def prwarn(msg: str, *args: Any, **kwargs: Any) -> None:
    logger.warning(msg, *args, **kwargs)


def prerror(msg: str, *args: Any, **kwargs: Any) -> None:
    logger.error(msg, *args, **kwargs)


def load_image_as_array(path: str) -> np.ndarray:
    """Load .npy or image file (PNG/JPEG etc.) as numpy array (2D or 3D)."""
    path = str(path)
    if path.lower().endswith(".npy"):
        return np.load(path)
    try:
        from PIL import Image
        img = Image.open(path)
        arr = np.array(img)
        if arr.ndim == 3 and arr.shape[-1] == 4:
            arr = arr[..., :3]
        return arr
    except ImportError:
        raise RuntimeError("Pillow required to load image files. Install with: uv add pillow")


def normalize_image(image: np.ndarray) -> np.ndarray:
    mean = np.mean(image)
    std = np.std(image)
    lower = max(0, mean - 3 * std)
    return np.clip(image, lower, mean + 3 * std).astype(image.dtype)


def generate_token() -> str:
    return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()[:8]


def sort_categories(
    df_full: pd.DataFrame,
    column: str,
    df_filtered: pd.DataFrame | None = None,
) -> np.ndarray:
    if df_filtered is None:
        df_filtered = df_full
    cats = df_filtered[column].unique()

    def to_sort_key(x: Any) -> Any:
        try:
            return float(x)
        except (ValueError, TypeError):
            return x

    order = np.argsort([to_sort_key(c) for c in cats])
    return cats[order]


def create_histogram_figure(df: pd.DataFrame, column_name: str):  # noqa: ANN201
    n = len(df)
    nbins = min(max(n // 10, 5), 1000)
    fig = px.histogram(df, x=column_name, nbins=nbins)
    fig.update_traces(opacity=0.6)
    fig.update_layout(
        height=100,
        margin=dict(t=10, l=10, r=10, b=10),
        xaxis=dict(title=column_name, title_font=dict(size=14)),
    )
    return fig

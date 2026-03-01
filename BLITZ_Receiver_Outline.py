# BLITZ receiver outline – contract/structure only. Do not import in WOLKE.
# Implementation lives in BLITZ. See BLITZ_Receiver_Contract.md for protocol details.
# Section "Implementierungsvorschlag fuer BLITZ (Index + Cache)" describes index/cache logic.

from pathlib import Path
from typing import Any

# -----------------------------------------------------------------------------
# Payload: {"file_name": str, "index": int | None}. index nur bei Tabellenklick
# (__selection__.npy); dann kein erneuter GET – Cache nutzen und arr[index] anzeigen.
# -----------------------------------------------------------------------------


class _WebSocket:
    """Connects to WOLKE via Socket.IO; on 'send_file_message' emits (file_name, index?)."""

    def __init__(self, target_address: str) -> None: ...
    def listen(self) -> None: ...
    # message payload: file_name (str), optional index (int)


class _WebDownloader:
    """GET {target}; on 200 write body to temp .npy, emit Path; else emit None."""

    def __init__(self, target_address: str) -> None: ...
    def download(self) -> None: ...


class WebDataLoader:
    """
    start() -> listen ws; on send_file_message:
      - file_name + optional index.
      - If file_name == "__selection__.npy" and index is set: use _selection_array cache
        (arr[index]); only GET if cache empty. Else: GET, then cache = arr, emit arr[index] or arr[0].
      - If file_name is normal path: clear cache, GET, emit loaded image.
    stop() quits threads.
    """

    def __init__(self, target_address: str, token: str, **kwargs: Any) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...

    # Suggested internal state for BLITZ (debate as needed):
    # _selection_array: np.ndarray | None  # last loaded __selection__.npy, shape (N, H, W, C) or (N, H, W)
    # On message: if file_name == "__selection__.npy" and index is not None:
    #   if _selection_array is not None: emit image_received(_selection_array[index])
    #   else: GET __selection__.npy, _selection_array = arr, emit image_received(arr[index])
    # On any other file_name: _selection_array = None, then GET and emit as today.

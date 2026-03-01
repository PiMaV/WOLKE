# BLITZ receiver outline – contract/structure only. Do not import in WOLKE.
# Implementation lives in BLITZ. See BLITZ_Receiver_Contract.md for protocol details.

from pathlib import Path


class _WebSocket:
    """Connects to WOLKE via Socket.IO; emits file_name on 'send_file_message'."""

    def __init__(self, target_address: str) -> None: ...
    def listen(self) -> None: ...


class _WebDownloader:
    """GET {target}; on 200 write body to temp .npy, emit Path; else emit None."""

    def __init__(self, target_address: str) -> None: ...
    def download(self) -> None: ...


class WebDataLoader:
    """
    start() -> listen ws; on file_name -> GET {base}/{token}?filename={file_name};
    load path via DataLoader -> emit image. stop() quits threads.
    """

    def __init__(self, target_address: str, token: str, **kwargs) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...

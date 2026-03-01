"""
BLITZ endpoint: GET /<token>?filename=... returns single .npy file; Socket.IO send_file_message.
Uses AppState for config. Always active. Contract: BLITZ_Receiver_Contract.md.
"""
import io
import os
from typing import TYPE_CHECKING

import numpy as np
from flask import abort, request, send_file

from wolke.utils import load_image_as_array, normalize_image, prerror, prinfo, prwarn

if TYPE_CHECKING:
    from wolke.state import AppState


class BlitzHandler:
    def __init__(self, server, socketio, state: "AppState"):
        self.server = server
        self.socketio = socketio
        self.state = state
        self._register_routes()
        self._register_socketio_events()

    def _register_routes(self) -> None:
        self.server.add_url_rule(
            "/<token>",
            view_func=self._get_file,
            methods=["GET"],
        )

    def _get_file(self, token: str):
        if token != self.state.token:
            prwarn("BLITZ - Invalid or missing token.")
            return abort(404)
        file_name = request.args.get("filename")
        if not file_name:
            prwarn("BLITZ - Missing filename query.")
            return abort(400)
        root = self.state.image_base_dir
        rel_col = self.state.relative_filepath_column

        if file_name == "__selection__.npy":
            return self._send_packed_selection(root, rel_col)

        safe_path = os.path.abspath(os.path.join(root, file_name))
        if not safe_path.startswith(os.path.abspath(root)):
            return abort(403)
        if not os.path.isfile(safe_path):
            prwarn(f"BLITZ - File not found: {safe_path}")
            return abort(404)
        try:
            arr = load_image_as_array(safe_path)
            if self.state.normalize_images:
                arr = self._normalize_arr(arr)
            buf = io.BytesIO()
            np.save(buf, arr)
            buf.seek(0)
            prinfo(f"BLITZ - Sending file: {file_name}")
            return send_file(
                buf,
                mimetype="application/octet-stream",
                download_name=os.path.basename(file_name) or "data.npy",
            )
        except Exception as e:
            prerror(f"BLITZ - Error: {e}")
            return abort(400)

    def _normalize_arr(self, arr: np.ndarray) -> np.ndarray:
        if arr.ndim == 3 and arr.shape[-1] in (3, 4):
            return np.stack(
                [normalize_image(arr[..., c]) for c in range(arr.shape[-1])],
                axis=-1,
            )
        if arr.ndim == 3:
            return np.array([normalize_image(arr[i]) for i in range(arr.shape[0])])
        return normalize_image(arr)

    def _send_packed_selection(self, root: str, rel_col: str):
        """Serve current selection as one stacked NumPy array (N, H, W, C) or (N, H, W)."""
        rows = getattr(self.state, "selected_rows", None) or []
        if not rows:
            prwarn("BLITZ - __selection__.npy requested but no selection.")
            return abort(404)
        arrays = []
        for row in rows:
            rel_path = row.get(rel_col)
            if not rel_path:
                continue
            safe = os.path.abspath(os.path.join(root, rel_path))
            if not safe.startswith(os.path.abspath(root)) or not os.path.isfile(safe):
                continue
            try:
                arr = load_image_as_array(safe)
                if arr.ndim == 3 and arr.shape[-1] not in (3, 4):
                    image_number = row.get("image_number", 0)
                    arr = arr[image_number]
                arrays.append(arr)
            except Exception as e:
                prerror(f"BLITZ - Skip image {rel_path}: {e}")
        if not arrays:
            prwarn("BLITZ - No valid images in selection.")
            return abort(404)
        try:
            stacked = np.stack(arrays, axis=0)
            if self.state.normalize_images:
                stacked = np.array([self._normalize_arr(stacked[i]) for i in range(stacked.shape[0])])
            buf = io.BytesIO()
            np.save(buf, stacked)
            buf.seek(0)
            prinfo(f"BLITZ - Sending packed selection: {stacked.shape}")
            return send_file(
                buf,
                mimetype="application/octet-stream",
                download_name="selection.npy",
            )
        except Exception as e:
            prerror(f"BLITZ - Error packing selection: {e}")
            return abort(400)

    def _register_socketio_events(self) -> None:
        self.socketio.on_event("connect", self._on_connect)
        self.socketio.on_event("disconnect", self._on_disconnect)
        self.socketio.on_event("viewer_index", self._on_viewer_index)
        self.socketio.on_error_default(self._on_error)
        self.socketio.on_event("*", self._catch_all)

    def _on_viewer_index(self, data: dict) -> None:
        """BLITZ sends current frame index; WOLKE syncs table selection (Contract: viewer_index)."""
        idx = data.get("index")
        if isinstance(idx, int) and idx >= 0:
            self.state.viewer_index = idx
            prinfo("BLITZ - viewer_index: %s", idx)

    def _on_connect(self) -> None:
        prinfo("BLITZ - Client connected")
        self.socketio.emit("Connected successfully")

    def _on_disconnect(self) -> None:
        prinfo("BLITZ - Client disconnected")

    def _on_error(self, e) -> None:
        prerror(f"BLITZ - Error: {e}")

    def _catch_all(self, event: str, data) -> None:
        prinfo(f"BLITZ - Event: {event} with data: {data}")

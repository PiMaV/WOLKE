# BLITZ Receiver Contract (WOLKE → BLITZ)

Reference for how BLITZ (viewer) receives data provided by WOLKE. Not meant to be imported in WOLKE. Code lives in BLITZ; this doc describes the protocol so WOLKE can stay compatible.

## Transport

- **Socket.IO** (WebSocket): BLITZ connects to WOLKE server URL (`http` → `ws`).
- **HTTP GET**: BLITZ downloads file by token + filename query.

## Socket.IO flow

1. BLITZ connects to `target_address` (http→ws).
2. Server may send `"Connected successfully"` → BLITZ logs, continues.
3. Server sends **`"send_file_message"`** with payload `{"file_name": "<filename>"}`.
4. BLITZ then downloads the file via HTTP (see below). Other message types → BLITZ may abort.

## HTTP download

- **URL**: `{target_address}/{token}?filename={file_name}` (trailing slash on base if needed).
- **Method**: GET.
- **Response**: 200 → body is file content (e.g. `.npy`); BLITZ writes to temp file, loads via DataLoader, emits result; then deletes temp file.
- **Failure**: no connection / non-200 → emit `None` or abort.

## Message / URL contract (WOLKE must provide)

| Item | Value |
|------|--------|
| Socket event name | `send_file_message` |
| Payload key | `file_name` (string) |
| Download URL | `{base}/{token}?filename={file_name}` |
| File format | e.g. `.npy` (consumed as NumPy in BLITZ) |

## BLITZ-side settings (for reference only)

- `web/connect_attempts`, `web/connect_timeout`, `web/download_attempts`.
- Used only in BLITZ; WOLKE does not need these keys.

## Minimal class outline (BLITZ side)

```
_WebSocket(target_address)
  - message_received(file_name | None)
  - listen() → connect ws, loop: on "send_file_message" emit message[1]["file_name"]

_WebDownloader(target_address)
  - download_finished(Path | None)
  - download() → GET target, write .npy temp, emit path or None

WebDataLoader(target_address, token, **load_kwargs)
  - image_received(image | None)
  - start() → _start_listening (ws thread)
  - stop() → stop listening, quit threads
  - Flow: listen → file_name → build URL → download → DataLoader.load(path) → image_received
```

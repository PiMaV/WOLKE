# WOLKE — Web-Oriented Layout for Knowledge Exploration

Browser dashboard for a **DAMPF** SQLite metadata database: filter, select, plot, and hand chosen files to **BLITZ** as NumPy arrays.

**WETTER pipeline:** `Raw Data → DAMPF → KEIM → WOLKE → BLITZ`

Overview and module links: **[wetter.mess.engineering](https://wetter.mess.engineering)**

[Download the latest release](https://github.com/PiMaV/WOLKE/releases/latest) (Windows `.exe` and Linux binary).

## Install and run (sample data)

```bash
git clone https://github.com/PiMaV/WOLKE.git
cd WOLKE
uv sync
uv run python scripts/generate_sample_data.py
cp config.ini.example config.ini
uv run python -m wolke
```

[uv](https://docs.astral.sh/uv/) is recommended. Without it: `pip install -r requirements.txt`, then `python -m wolke` in a virtualenv.

The browser opens on port 8050 (override with `WOLKE_PORT`). Config path: `config.ini` in the working directory / repo root, or `WOLKE_CONFIG`.

## Your own DAMPF database

Edit `config.ini`:

```ini
[data]
db_filename = sample_data/sample.db
table_name = sample_table
relative_filepath_column = relativ_npy_path

[general]
debug = False
port = 8050

[plot]
x = mean
y = std
color = sharpness
plot_marginals = violin
```

- `db_filename`: SQLite path (relative to the config file, or absolute).
- `relative_filepath_column`: column with paths to `.npy` / PNG / JPEG relative to the DB directory.
- `WOLKE_PORT` / `WOLKE_DEBUG` override port and debug.

WOLKE displays `.npy` and raster images; BLITZ still receives NumPy (images are converted on fetch).

## BLITZ link

On selection WOLKE sends `send_file_message` with `file_name` (relative path). BLITZ loads `GET {base}/{token}?filename={file_name}`. See `BLITZ_Receiver_Contract.md`.

## Standalone binary

```bash
uv sync --extra dev
uv run pyinstaller wolke.spec
```

Output: `dist/WOLKE.exe` (Windows) or `dist/WOLKE` (Linux). Put `config.ini` next to the binary (or set `WOLKE_CONFIG`). Tag `v*` on GitHub publishes `WOLKE.exe` and `WOLKE-linux-x86_64`.

## License

GNU GPL v3. See [LICENSE](LICENSE).

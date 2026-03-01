# WOLKE

**Web-Oriented Layout for Knowledge Exploration** – visualisiert Metadaten aus einer SQL-Datenbank, ermoeglicht dynamische Filterung und Selektion und liefert NumPy-Daten an den BLITZ-Viewer.

## Pipeline

- **DAMPF** (extern): Durchlaeuft Ordnerstrukturen und erzeugt eine **SQLite-Metadaten-Datenbank**.
- **WOLKE**: Liest diese DB, stellt Metadaten im Browser dar, Nutzer filtert und waehlt; optional Verbindung mit BLITZ.
- **BLITZ**: Bild-Viewer; kann sich jederzeit mit WOLKE verbinden (lokal oder Remote) und erhaelt ausgewaehlte .npy-Daten (Socket.IO + HTTP, siehe `BLITZ_Receiver_Contract.md`).

## Installation (uv)

[uv](https://docs.astral.sh/uv/) installieren, dann im Repo-Root:

```bash
git clone <repo>
cd WOLKE
uv sync
```

Damit wird eine virtuelle Umgebung angelegt und Abhaengigkeiten aus `pyproject.toml` installiert. Ohne uv: `pip install -r requirements.txt` (mit aktivierter venv).

## Starten

Aus dem Repo-Root (mit vorhandenem `config.ini`):

```bash
uv run python -m wolke
```

Ohne uv: `python -m wolke` (mit aktivierter venv).

Der Browser oeffnet sich automatisch. Ohne eigene Config wird die Beispiel-Config genutzt, falls `sample_data/config.ini.example` oder `config.ini` (mit Verweis auf `sample_data/sample.db`) vorhanden ist.

## Sample-Daten (Out-of-the-Box)

Strukturierte Beispieldaten zum sofortigen Testen und explorativen Erkunden:

- **Struktur:** `sample_data/images/set_A/`, `set_B/`, `set_C/` mit PNG-Bildern (Pseudobilder). Die Metadaten-DB verweist auf diese Pfade – wie von DAMPF erzeugt.
- **DB:** `sample_data/sample.db` mit Spalten id, relativ_npy_path (Pfad zu PNG), mean, std, sharpness, position, entropy, label.
- **Neu erzeugen:** `uv run python scripts/generate_sample_data.py` – erzeugt/ueberschreibt DB und PNGs in den Unterordnern.

WOLKE zeigt .npy und PNG/JPEG; BLITZ erhaelt die Daten weiterhin als NumPy (PNG/JPEG werden beim Abruf konvertiert). Die mitgelieferte `config.ini` zeigt auf `sample_data/sample.db`.

## Config

`config.ini` (im Repo-Root oder Pfad ueber Umgebungsvariable `WOLKE_CONFIG`):

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

- `db_filename`: Pfad zur SQLite-DB (relativ zum aktuellen Arbeitsverzeichnis oder absolut).
- `relative_filepath_column`: Spalte in der DB mit relativen Pfaden zu .npy-Dateien (Basisverzeichnis = Verzeichnis der DB-Datei).
- Optional: `WOLKE_PORT`, `WOLKE_DEBUG` ueberschreiben Port/Debug.

## EXE-Build (Windows)

Eine ausfuehrbare Datei bauen (uv installiert PyInstaller in die Umgebung):

```bash
uv sync --extra dev
uv run pyinstaller wolke.spec
```

Ergebnis: `dist/WOLKE.exe`. Beim Start wird der Server gestartet und der Browser geoeffnet.

- **config.ini** muss neben `WOLKE.exe` liegen (oder `WOLKE_CONFIG` auf einen gueltigen Config-Pfad zeigen).
- Unter Linux/macOS: `./scripts/build_exe.sh` erzeugt ein Binary in `dist/`.

## Projektstruktur

```
wolke/
  __init__.py
  __main__.py       # Einstieg: Server + Browser
  config.py         # Zentrale Config
  state.py          # AppState (keine Globals)
  data/
    loader.py       # DB laden, Kategorien/Numerics
    schema.py       # DAMPF-Schema (Dokumentation)
  web/
    app.py         # Dash-App erstellen
    layout.py      # UI-Layout
    callbacks.py   # Alle Callbacks
    plotter.py     # Scatter/3D
    blitz.py       # BLITZ-Endpoint (Socket.IO + GET .npy)
scripts/
  generate_sample_data.py   # Sample-DB + strukturierte PNGs in Unterordnern
  build_exe.bat / build_exe.sh
sample_data/        # Beispiel-DB + images/set_A|B|C/*.png (optional)
config.ini          # Beispiel-Config
wolke.spec          # PyInstaller
```

## BLITZ-Anbindung

- WOLKE sendet bei Auswahl `send_file_message` mit `file_name` (relativer Pfad).
- BLITZ laedt die Datei per GET: `{base}/{token}?filename={file_name}`.
- Details: `BLITZ_Receiver_Contract.md`, Referenz-Outline: `BLITZ_Receiver_Outline.py` (gehoert zu BLITZ, nicht in WOLKE importieren).

## Lizenz

Siehe `LICENSE`.

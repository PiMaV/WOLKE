# WOLKE Viewer Contract (Push / Download)

**Gemeinsame Referenz fuer WOLKE, DAMPF und BLITZ.** Dieses Dokument definiert (1) die **Datenquelle** (DB-Struktur, die DAMPF liefert und WOLKE erwartet) und (2) das **Protokoll** zwischen WOLKE (Server) und einem Viewer (DAMPF, BLITZ oder andere). Eine identische Kopie kann in DAMPF und BLITZ als Referenz liegen; WOLKE implementiert die Server-Seite, Viewer die Client-Seite.

---

## Datenquelle: DB-Struktur (DAMPF → WOLKE)

Damit WOLKE die Metadaten anzeigen und Dateien an den Viewer senden kann, muss DAMPF eine **SQLite-Datenbank** und die referenzierten Dateien liefern. WOLKE konfiguriert Tabellen- und Spaltennamen ueber `config.ini`; DAMPF muss sich an folgende Struktur halten.

### Pflicht

| Anforderung | Beschreibung |
|-------------|--------------|
| **Eine Tabelle** | Mindestens eine Tabelle (Name in WOLKE-Config: `[data] table_name`, z.B. `sample_table`). |
| **Pfad-Spalte** | Eine Spalte mit **relativen Pfaden** zu den Bild-/Daten-Dateien (z.B. `.npy`, PNG, JPEG). Spaltenname in Config: `[data] relative_filepath_column` (z.B. `relativ_npy_path`). |
| **Basisverzeichnis** | Alle Pfade sind **relativ zum Verzeichnis der DB-Datei**. WOLKE loest `{DB-Verzeichnis}/{relativer_Pfad}`. |

### Optional, aber empfohlen

| Anforderung | Beschreibung |
|-------------|--------------|
| **id** | Ganzzahl-Spalte (z.B. fuer Plot-Selektion). |
| **Numerische Spalten** | z.B. `mean`, `std`, `sharpness`, `position`, `entropy` – fuer Scatter/Filter in WOLKE. |
| **Kategorische Spalten** | z.B. `label` – fuer Gruppierung/Filter. |

### Beispiel-Schema (DAMPF kann so liefern)

```sql
CREATE TABLE sample_table (
    id INTEGER PRIMARY KEY,
    relativ_npy_path TEXT NOT NULL,
    mean REAL,
    std REAL,
    sharpness REAL,
    position REAL,
    entropy REAL,
    label TEXT
);
```

- **relativ_npy_path**: z.B. `images/set_A/0.png` oder `data/scan_001.npy` – relativ zum Ordner, in dem die DB-Datei liegt.
- Unterordner (z.B. `images/set_A/`, `images/set_B/`) sind erlaubt und werden von WOLKE so aufgeloest.

### WOLKE-Config (Referenz fuer DAMPF)

In `config.ini` gibt WOLKE vor, welche DB und welche Spalten genutzt werden:

```ini
[data]
db_filename = sample_data/sample.db
table_name = sample_table
relative_filepath_column = relativ_npy_path
```

DAMPF erzeugt die DB und die Dateien so, dass diese Pfade und Spalten existieren; dann weiss WOLKE, was es laden und an den Viewer senden kann.

---

## Rollen

| Rolle   | Beschreibung |
|--------|----------------|
| **Server (WOLKE)** | Stellt Socket.IO und HTTP bereit, sendet Datei-Benachrichtigungen, liefert Dateien per GET aus. |
| **Client (Viewer)** | DAMPF, BLITZ o.ae. – verbindet sich per Socket.IO, reagiert auf `send_file_message`, laedt Dateien per HTTP. |

---

## Transport

- **Socket.IO (WebSocket)**: Viewer verbindet sich mit der WOLKE-Server-URL (`http` → `ws`).
- **HTTP GET**: Viewer laedt eine Datei per Token + Dateiname als Query-Parameter.

---

## Socket.IO Ablauf

1. Viewer verbindet sich mit `target_address` (z.B. `http://host:port` → WebSocket).
2. Server kann `"Connected successfully"` senden → Viewer kann loggen, weitermachen.
3. Server sendet **`"send_file_message"`** mit Payload `{"file_name": "<filename>"}` oder `{"file_name": "<filename>", "index": <int>}` (siehe unten).
4. Viewer laedt die Datei per HTTP (siehe unten), sofern noetig; bei gesendetem **index** kann der Viewer das bereits geladene Paket nutzen und nur den Anzeige-Index wechseln (kein erneuter Download). Andere Message-Typen → Viewer kann ignorieren oder abbrechen.

---

## HTTP-Download

- **URL**: `{target_address}/{token}?filename={file_name}` (ggf. trailing slash an der Base-URL).
- **Method**: GET.
- **Response 200**: Body ist der Datei-Inhalt (z.B. `.npy`). Viewer schreibt in Temp-Datei, laedt (z.B. via DataLoader), gibt Ergebnis aus, loescht Temp-Datei.
- **Fehler**: Keine Verbindung / nicht 200 → Viewer gibt `None` zurueck oder bricht ab.

---

## Vertrag (Message / URL) – Server muss liefern, Client muss nutzen

| Item            | Wert |
|-----------------|------|
| Socket-Event    | `send_file_message` |
| Payload-Key     | `file_name` (string); optional **`index`** (int, 0-basiert) |
| Download-URL    | `{base}/{token}?filename={file_name}` |
| Dateiformat    | z.B. `.npy` (in BLITZ als NumPy geladen; DAMPF/BLITZ je nach Bedarf). |

### Mehrfachauswahl: Paket als eine NumPy-Matrix

Wenn im Scatter mehrere Punkte ausgewaehlt werden, sendet WOLKE **ein** Event mit `file_name: "__selection__.npy"`. Der Viewer laedt dann **eine** Datei unter `?filename=__selection__.npy`. Der Response-Body ist eine **gepackte NumPy-Datei**:

- **Shape**: `(N, H, W, C)` bei RGB(A)-Bildern, sonst `(N, H, W)`.
- **Reihenfolge**: Entspricht der Reihenfolge der ausgewaehlten Zeilen in der WOLKE-Tabelle (Index 0 = erste Zeile, 1 = zweite, …).
- Einzelauswahl: WOLKE sendet weiterhin den konkreten Dateinamen (z.B. `images/set_A/0.png`), kein Paket.

Viewer (DAMPF/BLITZ) koennen einheitlich: bei `file_name == "__selection__.npy"` die geladene Array-Shape auswerten und `arr[0]`, `arr[1]`, … als Einzelbilder nutzen.

### Index-Nachricht (ohne erneuten Download)

Wenn der Nutzer **in der unteren Tabelle eine Zelle anklickt** (Auswahl bleibt mehrfach), sendet WOLKE **nur den Index** im gleichen Event: `{"file_name": "__selection__.npy", "index": <int>}`. Es wird **keine neue Datei** ueber HTTP ausgeliefert – der Viewer hat das Paket bereits. Der Viewer soll:

- bei `file_name === "__selection__.npy"` und vorhandenem **`index`**: das bereits geladene Array nutzen und **nur** `arr[index]` anzeigen (kein erneuter GET);
- wenn das Paket noch nicht geladen ist: zuerst `?filename=__selection__.npy` laden, dann `arr[index]` anzeigen.

Damit reduziert sich der Traffic beim Durchklicken der Tabelle auf ein kleines Socket-Event mit Index.

#### Implementierungsvorschlag fuer BLITZ (Index + Cache, zur Debatte)

- **Cache**: Ein Objekt/Variable `_selection_array: np.ndarray | None` (oder `_packed_cache`) speichert das zuletzt geladene `__selection__.npy`-Array. Wird bei neuem `file_name` (z.B. Einzeldatei oder neues Paket) zurueckgesetzt/ersetzt.
- **Bei Empfang von `send_file_message`:**
  1. `file_name = payload["file_name"]`; `index = payload.get("index")` (optional, int).
  2. **Falls `file_name == "__selection__.npy"` und `index` ist gesetzt:**
     - Wenn `_selection_array` bereits geladen: sofort `image_received(_selection_array[index])` aufrufen, **kein** HTTP-Request.
     - Sonst: einmalig GET `?filename=__selection__.npy`, Array laden, in `_selection_array` speichern, dann `image_received(_selection_array[index])`.
  3. **Falls `file_name == "__selection__.npy"` und `index` fehlt:** wie bisher – GET, Array laden, `_selection_array = arr`, dann z.B. `image_received(arr[0])` oder gesamtes Paket weiterreichen.
  4. **Falls `file_name` eine normale Datei ist:** `_selection_array = None` (Cache invalide), GET wie bisher, `image_received(loaded)`.

Damit bleibt die bestehende Logik erhalten; nur bei `__selection__.npy` + `index` wird der Cache genutzt und kein zweiter Download ausgeloest. Zur Debatte: ob BLITZ ein einzelnes Bild (`arr[index]`) oder z.B. (array, index) an die Anzeige uebergibt, bleibt dem BLITZ-Design ueberlassen.

### Viewer-Index zurueck an WOLKE (Sync Tabelle)

Wenn der Nutzer **im Viewer (BLITZ) den Frame-Index aendert** (Slider/Spinbox/Timeline), sendet der Viewer ein Event an den Server, damit WOLKE die Tabellenzeile anzeigen kann.

| Item            | Wert |
|-----------------|------|
| Socket-Event    | `viewer_index` (Viewer → Server) |
| Payload         | `{"index": <int>}` (0-basiert) |
| Server (WOLKE)  | Sollte auf `viewer_index` hoeren und die Tabellenauswahl/Scroll auf die Zeile `index` setzen. |

---

## Client-seitige Einstellungen (nur Viewer)

- z.B. `web/connect_attempts`, `web/connect_timeout`, `web/download_attempts`.
- Werden nur in DAMPF/BLITZ verwendet; WOLKE braucht diese Keys nicht.

---

## Minimale Klassen-Uebersicht (Viewer-Seite, BLITZ/DAMPF)

```
_WebSocket(target_address)
  - message_received(file_name, index?)
  - listen() → connect ws, loop: on "send_file_message" emit message[1]["file_name"], optional message[1]["index"]

_WebDownloader(target_address)
  - download_finished(Path | None)
  - download() → GET target, write .npy temp, emit path or None

WebDataLoader(target_address, token, **load_kwargs)
  - image_received(image | None)   # oder (array, index) bei Paket – BLITZ-intern
  - _selection_array: np.ndarray | None   # Cache fuer __selection__.npy
  - start() → _start_listening (ws thread)
  - stop() → stop listening, quit threads
  - Flow: listen → file_name [, index]
    → wenn __selection__.npy + index und Cache voll: image_received(cache[index])
    → sonst: build URL → download → load → cache ggf. setzen → image_received(...)
```

---

## Verwendung in den Projekten

- **DAMPF**: Erzeugt SQLite-DB und Dateien gemaess Abschnitt **Datenquelle: DB-Struktur**. Tabellen- und Spaltennamen koennen mit WOLKE-Config uebereinstimmen (z.B. `sample_table`, `relativ_npy_path`). Kann ausserdem als Viewer dieses Contract nutzen (Connect, `send_file_message`, Download).
- **WOLKE**: Implementiert Server (Socket.IO + HTTP-Endpoint). Liest die von DAMPF gelieferte DB; haelt sich an Event-Namen, Payload und URL-Format aus diesem Contract.
- **BLITZ**: Kopie dieses Files als Referenz; Implementierung des Viewers (Connect, `send_file_message` hoeren, Download-URL bauen, GET, Datei verarbeiten) gemaess obiger Spezifikation.

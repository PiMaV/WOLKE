"""
Expected DB schema for DAMPF compatibility (documentation only).
WOLKE expects a SQLite DB with at least one table containing:
- A column with relative paths to image/data files (e.g. relativ_npy_path):
  .npy (NumPy arrays) or PNG/JPEG. Paths are relative to the DB directory.
- An optional id column (used for plot selection).
- Numeric and/or categorical columns for plotting/filtering.
Base directory for resolving paths is the directory of the DB file, or set in config.
Structured subfolders (e.g. images/set_A/, images/set_B/) are supported and referenced in the DB.
"""

"""
Generate sample SQLite DB and structured image data (PNG/JPEG in subfolders) for WOLKE.
Reproducible, CI-friendly. Run from repo root: uv run python scripts/generate_sample_data.py

One semantic shape per set, with controlled variance:
- set_A: rotating triangle (same shape, rotation varies).
- set_B: circle with varying translation and size.
- set_C: square with different scale in x and y (rectangles of varying aspect ratio).
"""
import math
import os
import sqlite3
import numpy as np

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None
    ImageDraw = None

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_data")
IMAGES_BASE = os.path.join(SAMPLE_DIR, "images")
DB_PATH = os.path.join(SAMPLE_DIR, "sample.db")
TABLE_NAME = "sample_table"
REL_PATH_COL = "relativ_npy_path"
SUBSETS = ("set_A", "set_B", "set_C")
NUM_PER_SUBSET = 8
IMAGE_EXT = ".png"
CANVAS_SIZE = (64, 64)
H, W = CANVAS_SIZE[0], CANVAS_SIZE[1]
CENTER_X, CENTER_Y = W / 2.0, H / 2.0


def _ensure_pil():
    if Image is None or ImageDraw is None:
        raise RuntimeError("Pillow (PIL) required for PNG/JPEG sample data. Install with: uv add pillow")


def _draw_set_a_rotating_triangle(canvas: np.ndarray, rng: np.random.Generator) -> None:
    """Set A: one triangle, variance = rotation (angle). Base: equilateral, tip up."""
    # Base vertices: equilateral triangle around center, radius ~18
    radius = 18.0
    angle0 = rng.uniform(0, 2 * math.pi)
    vertices = []
    for k in range(3):
        a = angle0 + k * (2 * math.pi / 3)
        x = CENTER_X + radius * math.cos(a)
        y = CENTER_Y - radius * math.sin(a)
        vertices.append((x, y))
    gray = int(rng.integers(100, 220))
    img = Image.fromarray(canvas)
    draw = ImageDraw.Draw(img)
    draw.polygon([(int(v[0]), int(v[1])) for v in vertices], fill=gray, outline=None)
    np.copyto(canvas, np.asarray(img))


def _draw_set_b_circle_translation_size(canvas: np.ndarray, rng: np.random.Generator) -> None:
    """Set B: circle only; variance = translation (cx, cy) and size (radius)."""
    h, w = canvas.shape
    cx = int(rng.integers(w * 0.2, w * 0.8))
    cy = int(rng.integers(h * 0.2, h * 0.8))
    r = int(rng.integers(10, min(w, h) // 2 - 4))
    gray = int(rng.integers(100, 220))
    yy = np.arange(h, dtype=np.int32)
    xx = np.arange(w, dtype=np.int32)
    grid_y, grid_x = np.meshgrid(yy, xx, indexing="ij")
    inside = (grid_x - cx) ** 2 + (grid_y - cy) ** 2 <= r * r
    canvas[inside] = gray


def _draw_set_c_square_scaled_xy(canvas: np.ndarray, rng: np.random.Generator) -> None:
    """Set C: square base, variance = scale in x and y (different -> rectangle)."""
    half_base = 14.0
    sx = rng.uniform(0.45, 0.95)
    sy = rng.uniform(0.45, 0.95)
    hw_x = half_base * sx
    hw_y = half_base * sy
    x0 = int(CENTER_X - hw_x)
    y0 = int(CENTER_Y - hw_y)
    x1 = int(CENTER_X + hw_x)
    y1 = int(CENTER_Y + hw_y)
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W, x1)
    y1 = min(H, y1)
    gray = int(rng.integers(100, 220))
    canvas[y0:y1, x0:x1] = gray


def generate_one_image_for_subset(subset: str, rng: np.random.Generator) -> np.ndarray:
    """One shape per set: set_A rotating triangle, set_B circle (translation+size), set_C square (scale x/y)."""
    h, w = CANVAS_SIZE
    canvas = np.full((h, w), int(rng.integers(25, 55)), dtype=np.uint8)
    if subset == "set_A":
        _draw_set_a_rotating_triangle(canvas, rng)
    elif subset == "set_B":
        _draw_set_b_circle_translation_size(canvas, rng)
    else:
        _draw_set_c_square_scaled_xy(canvas, rng)
    return canvas


def main():
    _ensure_pil()
    rng = np.random.default_rng(42)
    rows = []
    row_id = 0

    for subset in SUBSETS:
        subdir = os.path.join(IMAGES_BASE, subset)
        os.makedirs(subdir, exist_ok=True)
        for i in range(NUM_PER_SUBSET):
            img_arr = generate_one_image_for_subset(subset, rng)
            rel_path = f"images/{subset}/{i}{IMAGE_EXT}"
            full_path = os.path.join(SAMPLE_DIR, rel_path)
            Image.fromarray(img_arr).save(full_path)

            mean_val = float(np.mean(img_arr))
            std_val = float(np.std(img_arr))
            sharpness_val = mean_val / (std_val + 1e-6) * 0.01
            rows.append({
                "id": row_id,
                REL_PATH_COL: rel_path,
                "mean": round(mean_val, 4),
                "std": round(std_val, 4),
                "sharpness": round(sharpness_val, 6),
                "position": row_id * 10,
                "entropy": round(float(rng.uniform(2, 10)), 4),
                "label": subset.replace("set_", ""),
            })
            row_id += 1

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY,
            {REL_PATH_COL} TEXT NOT NULL,
            mean REAL,
            std REAL,
            sharpness REAL,
            position REAL,
            entropy REAL,
            label TEXT
        )
    """)
    conn.commit()
    for r in rows:
        cur.execute(
            f"INSERT OR REPLACE INTO {TABLE_NAME} (id, {REL_PATH_COL}, mean, std, sharpness, position, entropy, label) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (r["id"], r[REL_PATH_COL], r["mean"], r["std"], r["sharpness"], r["position"], r["entropy"], r["label"]),
        )
    conn.commit()
    conn.close()
    total = len(rows)
    print(f"Generated {DB_PATH} and {total} image files in {IMAGES_BASE}")
    print(f"  Structure: images/set_A/, images/set_B/, images/set_C/ ({IMAGE_EXT})")


if __name__ == "__main__":
    main()

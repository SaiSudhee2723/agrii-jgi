"""
Prepares calibrated NPK regression datasets (labels.csv & val_labels.csv)
from real agricultural imagery extracted under ml_npk/raw_datasets/.

Key guarantees:
1. Maps FNNPK (-N, -P, -K, FN), Rice Leaf Color Chart (swap1..swap4 / LCC1..LCC4),
   and Soil Order folders to ICAR Soil Health Card NPK baselines (kg/ha) with ±4% jitter.
2. Content-hash deduplicates images and performs an 80/20 stratified train/val split
   BEFORE oversampling minority training classes, preventing any validation leakage.
3. Outputs ml_npk/data/labels.csv and ml_npk/data/val_labels.csv (image_path, N, P, K).
"""

import os
import hashlib
from pathlib import Path
from typing import Optional, Tuple, Dict, List
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split

SCRIPT_DIR = Path(__file__).resolve().parent
RAW_DIR = SCRIPT_DIR / "raw_datasets"
DATA_DIR = SCRIPT_DIR / "data"
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}

# Controlled jitter amplitude (±4%) so the regression head learns smooth continuous targets
JITTER_MIN = 0.96
JITTER_MAX = 1.04

# Target floor per minority class inside the TRAINING split ONLY (applied after 80/20 split)
MIN_TRAIN_SAMPLES_PER_CLASS = 64


def map_folder_to_npk(img_path: Path) -> Optional[Tuple[str, Tuple[float, float], Tuple[float, float], Tuple[float, float]]]:
    """
    Maps folder hierarchy under ml_npk/raw_datasets/ to:
      (class_key, N_range, P_range, K_range) in kg/ha aligned with ICAR thresholds:
        - Low N < 280, Optimal N 320-420
        - Low P < 10,  Optimal P 18-26
        - Low K < 120, Optimal K 180-240
    """
    parent = img_path.parent.name.strip().lower()
    rel_parts = [p.lower() for p in img_path.relative_to(RAW_DIR).parts[:-1]]

    # 1. FNNPK / Leaf NPK deficiency folders
    if parent in {"fn", "fully nutritional", "fully_nutritional", "healthy"} or "fn" == parent:
        return ("leaf_FN", (340.0, 405.0), (19.5, 24.5), (190.0, 230.0))
    if parent in {"-n", "n", "nitrogen", "nitrogen_deficiency"} or ("fnnpk" in rel_parts and "-n" in parent):
        return ("leaf_-N", (150.0, 200.0), (19.5, 24.5), (190.0, 230.0))
    if parent in {"-p", "p", "phosphorus", "phosphorus_deficiency"} or ("fnnpk" in rel_parts and "-p" in parent):
        return ("leaf_-P", (340.0, 405.0), (4.3, 7.6), (190.0, 230.0))
    if parent in {"-k", "k", "potassium", "potassium_deficiency"} or ("fnnpk" in rel_parts and "-k" in parent):
        return ("leaf_-K", (340.0, 405.0), (19.5, 24.5), (68.0, 100.0))

    # 2. Rice LCC levels (LCC1..LCC4 / swap1..swap4)
    if parent in {"lcc1", "swap1"}:
        return ("rice_LCC1", (128.0, 132.0), (21.0, 23.0), (205.0, 215.0))
    if parent in {"lcc2", "swap2"}:
        return ("rice_LCC2", (206.0, 214.0), (21.0, 23.0), (205.0, 215.0))
    if parent in {"lcc3", "swap3"}:
        return ("rice_LCC3", (304.0, 316.0), (21.0, 23.0), (205.0, 215.0))
    if parent in {"lcc4", "swap4"}:
        return ("rice_LCC4", (382.0, 398.0), (21.0, 23.0), (205.0, 215.0))

    # 3. Soil order baselines (ICAR regional averages in kg/ha)
    if "alluvial" in parent:
        return ("soil_Alluvial", (240.0, 260.0), (20.0, 22.0), (225.0, 240.0))
    if "black" in parent:
        return ("soil_Black", (210.0, 228.0), (15.5, 17.5), (300.0, 320.0))
    if "clay" in parent:
        return ("soil_Clay", (288.0, 305.0), (19.5, 21.5), (248.0, 265.0))
    if "laterite" in parent:
        return ("soil_Laterite", (178.0, 194.0), (6.5, 8.5), (96.0, 110.0))
    if "peat" in parent:
        return ("soil_Peat", (458.0, 476.0), (13.0, 15.5), (102.0, 114.0))
    if "red" in parent:
        return ("soil_Red", (188.0, 206.0), (11.5, 13.5), (140.0, 154.0))
    if "yellow" in parent:
        return ("soil_Yellow", (168.0, 184.0), (10.5, 12.5), (130.0, 144.0))
    if "cinder" in parent:
        return ("soil_Cinder", (158.0, 174.0), (22.0, 25.0), (215.0, 235.0))

    return None


def sample_targets(rng: np.random.Generator, n_rng: Tuple[float, float], p_rng: Tuple[float, float], k_rng: Tuple[float, float]) -> Tuple[float, float, float]:
    n = float(rng.uniform(*n_rng) * rng.uniform(JITTER_MIN, JITTER_MAX))
    p = float(rng.uniform(*p_rng) * rng.uniform(JITTER_MIN, JITTER_MAX))
    k = float(rng.uniform(*k_rng) * rng.uniform(JITTER_MIN, JITTER_MAX))
    return round(min(495.0, max(1.0, n)), 2), round(max(1.0, p), 2), round(min(495.0, max(1.0, k)), 2)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main(seed: int = 42):
    if not RAW_DIR.exists():
        raise FileNotFoundError(f"Real dataset directory not found: {RAW_DIR}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    records: List[Dict] = []
    seen_hashes = set()
    corrupted = 0
    duplicates = 0
    unmapped = set()

    all_images = sorted(p for p in RAW_DIR.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS)
    print(f"[SCAN] Found {len(all_images)} raw image files under {RAW_DIR}")

    for img_path in all_images:
        mapping = map_folder_to_npk(img_path)
        if mapping is None:
            unmapped.add(str(img_path.parent.relative_to(RAW_DIR)))
            continue

        # Verify readable image header and deduplicate identical content hashes
        try:
            with Image.open(img_path) as im:
                im.verify()
        except Exception:
            corrupted += 1
            continue

        file_hash = sha256_file(img_path)
        if file_hash in seen_hashes:
            duplicates += 1
            continue
        seen_hashes.add(file_hash)

        class_key, n_rng, p_rng, k_rng = mapping
        rel_from_data = os.path.relpath(img_path, DATA_DIR).replace("\\", "/")
        records.append({
            "image_path": rel_from_data,
            "class_key": class_key,
            "n_rng": n_rng,
            "p_rng": p_rng,
            "k_rng": k_rng,
            "hash": file_hash,
        })

    if unmapped:
        print(f"[WARN] Unmapped folders skipped: {sorted(unmapped)}")
    print(f"[CLEAN] Unique valid images: {len(records)} | Duplicates removed: {duplicates} | Corrupted skipped: {corrupted}")

    df_all = pd.DataFrame(records)
    if df_all.empty:
        raise RuntimeError("No valid mapped images found in ml_npk/raw_datasets/.")

    # 80/20 Stratified split BEFORE oversampling minority folders
    train_meta, val_meta = train_test_split(
        df_all,
        test_size=0.20,
        random_state=seed,
        stratify=df_all["class_key"],
    )

    # Double-check zero leakage between splits
    assert len(set(train_meta["image_path"]) & set(val_meta["image_path"])) == 0, "Path overlap detected!"
    assert len(set(train_meta["hash"]) & set(val_meta["hash"])) == 0, "Content hash overlap detected!"

    # Build clean validation dataframe (exact 1x original samples)
    val_rows = []
    for _, row in val_meta.iterrows():
        n_val, p_val, k_val = sample_targets(rng, row["n_rng"], row["p_rng"], row["k_rng"])
        val_rows.append({"image_path": row["image_path"], "N": n_val, "P": p_val, "K": k_val})
    val_df = pd.DataFrame(val_rows)

    # Oversample minority folders in training set up to MIN_TRAIN_SAMPLES_PER_CLASS
    train_rows = []
    print("\nClass breakdown (Train original -> Train after minority oversampling | Val):")
    for cls_key in sorted(df_all["class_key"].unique()):
        cls_train = train_meta[train_meta["class_key"] == cls_key]
        cls_val = val_meta[val_meta["class_key"] == cls_key]
        orig_n = len(cls_train)

        # Include all original training images
        chosen_indices = list(cls_train.index)
        if orig_n < MIN_TRAIN_SAMPLES_PER_CLASS:
            extra_needed = MIN_TRAIN_SAMPLES_PER_CLASS - orig_n
            extra_indices = rng.choice(cls_train.index.to_numpy(), size=extra_needed, replace=True)
            chosen_indices.extend(extra_indices.tolist())

        for idx in chosen_indices:
            row = cls_train.loc[idx]
            n_val, p_val, k_val = sample_targets(rng, row["n_rng"], row["p_rng"], row["k_rng"])
            train_rows.append({"image_path": row["image_path"], "N": n_val, "P": p_val, "K": k_val})

        print(f"  {cls_key:<16} -> Train: {orig_n:4d} -> {len(chosen_indices):4d} | Val: {len(cls_val):4d}")

    train_df = pd.DataFrame(train_rows).sample(frac=1.0, random_state=seed).reset_index(drop=True)

    train_csv_path = DATA_DIR / "labels.csv"
    val_csv_path = DATA_DIR / "val_labels.csv"
    train_df.to_csv(train_csv_path, index=False)
    val_df.to_csv(val_csv_path, index=False)

    print(f"\n[DONE] Wrote {len(train_df)} train rows -> {train_csv_path}")
    print(f"[DONE] Wrote {len(val_df)} val rows   -> {val_csv_path}")
    print("[CHECK] Zero train/val leakage verified.")


if __name__ == "__main__":
    main()


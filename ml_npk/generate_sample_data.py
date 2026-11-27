"""
Generates 200 synthetic color-calibrated soil & leaf samples + labels.csv
for immediate end-to-end RTX 4060 training & ONNX verification before dropping
in your real Kaggle / laboratory dataset.
"""

import os
import csv
import numpy as np
import cv2


def generate_synthetic_dataset(out_dir: str, num_samples: int = 200, seed: int = 42):
    rng = np.random.default_rng(seed)
    images_dir = os.path.join(out_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "labels.csv")

    rows = []
    H, W = 256, 256

    for i in range(num_samples):
        # Sample agronomic NPK ranges matching soil benchmarks (kg/ha)
        # N: 15..190, P: 6..85, K: 25..230
        n_val = float(np.round(rng.uniform(15.0, 190.0), 2))
        p_val = float(np.round(rng.uniform(6.0, 85.0), 2))
        k_val = float(np.round(rng.uniform(25.0, 230.0), 2))

        n_norm = (n_val - 15.0) / 175.0
        p_norm = (p_val - 6.0) / 79.0
        k_norm = (k_val - 25.0) / 205.0

        # Alternate between dark humus soil samples and crop leaf canopy samples
        is_soil = (i % 2 == 0)

        if is_soil:
            # Soil hue/darkness correlates with organic N, oxide/mineral P tint, and pale K silt tones
            base_r = 148 - 58 * n_norm + 16 * (1.0 - p_norm) + 12 * k_norm
            base_g = 112 - 42 * n_norm - 8 * (1.0 - p_norm) + 18 * k_norm
            base_b = 78 - 32 * n_norm + 14 * (1.0 - p_norm) - 10 * k_norm

            canvas = np.zeros((H, W, 3), dtype=np.float32)
            canvas[:, :, 0] = base_r
            canvas[:, :, 1] = base_g
            canvas[:, :, 2] = base_b

            # Granular soil texture + aggregate crumb noise
            fine_noise = rng.normal(0, 11.0, (H, W, 1))
            coarse = cv2.GaussianBlur(rng.normal(0, 18.0, (H // 4, W // 4, 1)), (5, 5), 0)
            coarse = cv2.resize(coarse, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
            canvas = canvas + fine_noise + coarse

            # Simulate organic specks (proportional to N)
            num_specks = int(20 + 140 * n_norm)
            for _ in range(num_specks):
                cx, cy = int(rng.integers(5, W - 5)), int(rng.integers(5, H - 5))
                rad = int(rng.integers(1, 4))
                cv2.circle(canvas, (cx, cy), rad, (42.0, 34.0, 26.0), -1)
        else:
            # Leaf chlorophyll & deficiency correlates:
            # Low N -> chlorotic yellow-green; High N -> rich emerald green
            # Low P -> subtle purplish anthocyanin tint; Low K -> warm scorched leaf margin
            base_r = 152 - 92 * n_norm + 26 * (1.0 - p_norm)
            base_g = 158 + 22 * n_norm - 36 * (1.0 - n_norm) - 12 * (1.0 - p_norm)
            base_b = 62 - 22 * n_norm + 28 * (1.0 - p_norm)

            canvas = np.zeros((H, W, 3), dtype=np.float32)
            canvas[:, :, 0] = base_r
            canvas[:, :, 1] = base_g
            canvas[:, :, 2] = base_b

            # Leaf venation gradient
            y_grid = np.linspace(-1, 1, H)[:, None]
            x_grid = np.linspace(-1, 1, W)[None, :]
            dist_edge = np.maximum(np.abs(x_grid), np.abs(y_grid))

            # Potassium deficiency creates marginal yellowing/browning near leaf outer border
            k_margin_mask = np.clip((dist_edge - 0.62) / 0.38, 0.0, 1.0) * (1.0 - k_norm)
            canvas[:, :, 0] += 65.0 * k_margin_mask
            canvas[:, :, 1] += 25.0 * k_margin_mask
            canvas[:, :, 2] -= 22.0 * k_margin_mask

            # Mild natural surface texture
            canvas += rng.normal(0, 6.0, (H, W, 3))

            # Central leaf midrib
            cv2.line(canvas, (W // 2, 10), (W // 2, H - 10), (base_r + 25, base_g + 28, base_b + 10), 3)

        # Mild natural ambient exposure scaling (tests color constancy robustness)
        ambient_scale = float(rng.uniform(0.88, 1.12))
        img_rgb = np.clip(canvas * ambient_scale, 0, 255).astype(np.uint8)
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

        rel_path = f"images/sample_{i:04d}.jpg"
        abs_path = os.path.join(out_dir, rel_path)
        cv2.imwrite(abs_path, img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 94])

        rows.append([rel_path, n_val, p_val, k_val])

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["image_path", "N", "P", "K"])
        writer.writerows(rows)

    print(f"[OK] Generated {num_samples} synthetic color-calibrated samples in: {images_dir}")
    print(f"[OK] Labels written to: {csv_path}")


if __name__ == "__main__":
    default_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    generate_synthetic_dataset(default_data_dir, num_samples=200)


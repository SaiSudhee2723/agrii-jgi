"""
PyTorch Dataset for Multimodal Soil/Leaf NPK Regression.
Expects labels.csv with columns: image_path, N, P, K.
Enforces color constancy preprocessing and color-preserving augmentations ONLY
(flips, 90-deg rotations, minor brightness jitter; zero hue/saturation shifts).
"""

import os
import pandas as pd
import numpy as np
import cv2
import torch
from torch.utils.data import Dataset
import albumentations as A

from preprocessing import (
    IMG_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD,
    apply_color_constancy,
    extract_hsv_lab_histogram,
)


def build_transforms(is_train: bool = True) -> A.Compose:
    """
    Strictly avoids Hue/Saturation/ChannelShuffle augmentations because pixel color
    directly encodes Nitrogen, Phosphorus, and Potassium concentrations.
    """
    if is_train:
        return A.Compose([
            A.Resize(IMG_SIZE, IMG_SIZE),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.RandomBrightnessContrast(brightness_limit=0.08, contrast_limit=0.08, p=0.4),
        ])
    return A.Compose([
        A.Resize(IMG_SIZE, IMG_SIZE),
    ])


class NPKVisionDataset(Dataset):
    def __init__(self, df: pd.DataFrame, data_root: str, is_train: bool = True):
        self.df = df.reset_index(drop=True)
        self.data_root = data_root
        self.transforms = build_transforms(is_train=is_train)

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]
        raw_path = str(row["image_path"])
        img_path = raw_path if os.path.isabs(raw_path) else os.path.join(self.data_root, raw_path)

        img_bgr = cv2.imread(img_path, cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise FileNotFoundError(f"Could not read image at {img_path}")

        # Pre-downscale high-res DSLR Kaggle images before CLAHE to prevent OOM and speed up CPU pipeline
        h, w = img_bgr.shape[:2]
        max_dim = max(h, w)
        if max_dim > 512:
            scale = 512.0 / float(max_dim)
            img_bgr = cv2.resize(img_bgr, (max(1, int(w * scale)), max(1, int(h * scale))), interpolation=cv2.INTER_AREA)

        # 1. Color constancy normalization (Gray-World + LAB L-CLAHE)
        cc_bgr = apply_color_constancy(img_bgr)
        img_rgb = cv2.cvtColor(cc_bgr, cv2.COLOR_BGR2RGB)

        # 2. Color-safe spatial & minor brightness augmentations
        augmented = self.transforms(image=img_rgb)
        aug_rgb = augmented["image"]

        # 3. Extract 54-bin HSV + LAB color histogram
        hist_vec = extract_hsv_lab_histogram(aug_rgb)

        # 4. Normalize RGB tensor for pretrained vision backbone
        img_f = aug_rgb.astype(np.float32) / 255.0
        img_f = (img_f - IMAGENET_MEAN) / IMAGENET_STD
        img_chw = np.transpose(img_f, (2, 0, 1)).astype(np.float32)

        target = np.array(
            [float(row["N"]), float(row["P"]), float(row["K"])],
            dtype=np.float32,
        )

        return (
            torch.from_numpy(img_chw),
            torch.from_numpy(hist_vec),
            torch.from_numpy(target),
        )


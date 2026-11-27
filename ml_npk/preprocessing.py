"""
Shared Color-Constancy Preprocessing & HSV+LAB Feature Extraction for NPK Vision.
Identical transforms are used in both PyTorch Dataset training and FastAPI ONNX serving.
"""

from typing import Tuple
import cv2
import numpy as np

IMG_SIZE = 224
HIST_DIM = 54  # 18 (H) + 9 (S) + 9 (V) + 9 (LAB-a) + 9 (LAB-b)

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def apply_color_constancy(img_bgr: np.ndarray) -> np.ndarray:
    """
    Applies Gray-World white balance followed by gentle LAB L-channel CLAHE.
    Preserves true chromaticity (a*, b* / Hue) while stabilizing ambient lighting.
    """
    img_f = img_bgr.astype(np.float32)
    b_mean, g_mean, r_mean = np.mean(img_f, axis=(0, 1))
    gray_mean = (b_mean + g_mean + r_mean) / 3.0 + 1e-6

    gains = np.array(
        [
            np.clip(gray_mean / (b_mean + 1e-6), 0.75, 1.35),
            np.clip(gray_mean / (g_mean + 1e-6), 0.75, 1.35),
            np.clip(gray_mean / (r_mean + 1e-6), 0.75, 1.35),
        ],
        dtype=np.float32,
    )
    balanced_bgr = np.clip(img_f * gains, 0, 255).astype(np.uint8)

    # Normalize luminance lightness only (leave chromatic a*, b* untouched)
    lab = cv2.cvtColor(balanced_bgr, cv2.COLOR_BGR2LAB)
    l_chan, a_chan, b_chan = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=1.8, tileGridSize=(8, 8))
    l_eq = clahe.apply(l_chan)
    lab_eq = cv2.merge((l_eq, a_chan, b_chan))
    return cv2.cvtColor(lab_eq, cv2.COLOR_LAB2BGR)


def extract_hsv_lab_histogram(img_rgb_uint8: np.ndarray) -> np.ndarray:
    """
    Extracts normalized 54-bin HSV + LAB chromaticity histogram vector from RGB uint8 image.
    H: 18 bins, S: 9 bins, V: 9 bins, LAB-a: 9 bins, LAB-b: 9 bins.
    """
    hsv = cv2.cvtColor(img_rgb_uint8, cv2.COLOR_RGB2HSV)
    lab = cv2.cvtColor(img_rgb_uint8, cv2.COLOR_RGB2LAB)

    h_hist = cv2.calcHist([hsv], [0], None, [18], [0, 180]).flatten()
    s_hist = cv2.calcHist([hsv], [1], None, [9], [0, 256]).flatten()
    v_hist = cv2.calcHist([hsv], [2], None, [9], [0, 256]).flatten()
    a_hist = cv2.calcHist([lab], [1], None, [9], [0, 256]).flatten()
    b_hist = cv2.calcHist([lab], [2], None, [9], [0, 256]).flatten()

    feats = []
    for h in (h_hist, s_hist, v_hist, a_hist, b_hist):
        total = float(h.sum()) + 1e-6
        feats.append((h / total).astype(np.float32))

    return np.concatenate(feats, axis=0)


def preprocess_bgr_for_inference(img_bgr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Preprocesses a raw OpenCV BGR image into CHW float32 tensor [3, 224, 224]
    and color histogram vector [54].
    """
    cc_bgr = apply_color_constancy(img_bgr)
    resized_bgr = cv2.resize(cc_bgr, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_AREA)
    img_rgb = cv2.cvtColor(resized_bgr, cv2.COLOR_BGR2RGB)

    hist_vec = extract_hsv_lab_histogram(img_rgb)

    img_norm = img_rgb.astype(np.float32) / 255.0
    img_norm = (img_norm - IMAGENET_MEAN) / IMAGENET_STD
    img_chw = np.transpose(img_norm, (2, 0, 1)).astype(np.float32)
    return img_chw, hist_vec


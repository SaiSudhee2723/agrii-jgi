"""
Module 1 Extension: ONNX Runtime NPK Vision Inference Service.
Loads backend/app/models/npk_model.onnx, runs the exact OpenCV color-constancy
(Gray-World + LAB L-CLAHE) and HSV+LAB 54-bin histogram preprocessing used during
PyTorch training, and predicts [Nitrogen, Phosphorus, Potassium] + agronomic statuses.
"""

import os
import io
import json
import base64
import logging
import threading
from typing import Tuple, Dict, Any, List, Optional
import numpy as np

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    import onnxruntime as ort
    ORT_AVAILABLE = True
except ImportError:
    ort = None
    ORT_AVAILABLE = False

from PIL import Image
from app.services.soil_service import SoilAnalysisService
from app.schemas.soil import NPKPredictionResponse, NPKStatusMap

logger = logging.getLogger("geosense.npk_inference")

IMG_SIZE = 224
HIST_DIM = 54
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models",
    "npk_model.onnx",
)
METADATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models",
    "model_metadata.json",
)


class NPKInferenceService:
    _session: Optional[Any] = None
    _metadata: Optional[Dict[str, Any]] = None
    _lock = threading.Lock()

    @classmethod
    def _get_metadata(cls) -> Dict[str, Any]:
        if cls._metadata is None:
            if os.path.exists(METADATA_PATH):
                try:
                    with open(METADATA_PATH, "r", encoding="utf-8") as f:
                        cls._metadata = json.load(f)
                except Exception as exc:
                    logger.warning(f"Failed to read model_metadata.json: {exc}")
                    cls._metadata = {"model_source": "unknown"}
            else:
                cls._metadata = {"model_source": "real_dataset"}
        return cls._metadata

    @classmethod
    def _get_session(cls):
        if not ORT_AVAILABLE:
            raise RuntimeError("onnxruntime is not installed in the backend environment.")
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Trained ONNX model not found at {MODEL_PATH}. Run ml_npk/train.py to export npk_model.onnx."
            )
        if cls._session is None:
            with cls._lock:
                if cls._session is None:
                    providers = ["CPUExecutionProvider"]
                    avail = ort.get_available_providers()
                    if "CUDAExecutionProvider" in avail:
                        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
                    cls._session = ort.InferenceSession(MODEL_PATH, providers=providers)
                    logger.info(f"Loaded NPK ONNX model from {MODEL_PATH} (providers: {cls._session.get_providers()})")
        return cls._session

    @classmethod
    def reload_model(cls):
        with cls._lock:
            cls._session = None
            cls._metadata = None

    @staticmethod
    def decode_base64_image(b64_str: str) -> bytes:
        if not b64_str or not b64_str.strip():
            raise ValueError("Empty base64 image payload.")
        raw = b64_str.strip()
        if "," in raw and raw.lower().startswith("data:"):
            raw = raw.split(",", 1)[1]
        try:
            return base64.b64decode(raw, validate=True)
        except Exception as exc:
            raise ValueError(f"Invalid base64 image string: {exc}") from exc

    @staticmethod
    def _apply_color_constancy(img_bgr: np.ndarray) -> np.ndarray:
        """Exact mirror of ml_npk/preprocessing.py apply_color_constancy."""
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

        lab = cv2.cvtColor(balanced_bgr, cv2.COLOR_BGR2LAB)
        l_chan, a_chan, b_chan = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=1.8, tileGridSize=(8, 8))
        l_eq = clahe.apply(l_chan)
        lab_eq = cv2.merge((l_eq, a_chan, b_chan))
        return cv2.cvtColor(lab_eq, cv2.COLOR_LAB2BGR)

    @staticmethod
    def _extract_hsv_lab_histogram(img_rgb_uint8: np.ndarray) -> np.ndarray:
        """Exact mirror of ml_npk/preprocessing.py extract_hsv_lab_histogram."""
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

    @classmethod
    def _preprocess_bytes(cls, image_bytes: bytes) -> Tuple[np.ndarray, np.ndarray, np.ndarray, int, int]:
        if OPENCV_AVAILABLE:
            arr = np.frombuffer(image_bytes, np.uint8)
            img_bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if img_bgr is None:
                raise ValueError("Could not decode image bytes. Ensure JPEG, PNG, or WEBP format.")
        else:
            pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img_rgb_raw = np.array(pil_img)
            img_bgr = img_rgb_raw[:, :, ::-1].copy()

        h, w = img_bgr.shape[:2]
        raw_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB) if OPENCV_AVAILABLE else img_bgr[:, :, ::-1]

        cc_bgr = cls._apply_color_constancy(img_bgr)
        resized_bgr = cv2.resize(cc_bgr, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_AREA)
        img_rgb = cv2.cvtColor(resized_bgr, cv2.COLOR_BGR2RGB)

        hist_vec = cls._extract_hsv_lab_histogram(img_rgb)

        img_norm = img_rgb.astype(np.float32) / 255.0
        img_norm = (img_norm - IMAGENET_MEAN) / IMAGENET_STD
        img_chw = np.transpose(img_norm, (2, 0, 1)).astype(np.float32)

        return (
            np.expand_dims(img_chw, axis=0),
            np.expand_dims(hist_vec, axis=0),
            raw_rgb,
            w,
            h,
        )

    @staticmethod
    def classify_npk_status(n: float, p: float, k: float) -> NPKStatusMap:
        """Classifies predicted kg/ha NPK concentrations using ICAR Soil Health Card thresholds."""
        n_stat = "Low" if n < 280.0 else ("High" if n > 460.0 else "Optimal")
        p_stat = "Low" if p < 10.0 else ("High" if p > 30.0 else "Optimal")
        k_stat = "Low" if k < 120.0 else ("High" if k > 280.0 else "Optimal")
        return NPKStatusMap(N=n_stat, P=p_stat, K=k_stat)

    @staticmethod
    def build_recommendations(n: float, p: float, k: float, status: NPKStatusMap) -> List[str]:
        recs = []
        if status.N == "Low":
            recs.append(f"Nitrogen estimated Low ({n:.1f} kg/ha): Plan split Urea or organic green manure top-dressing.")
        elif status.N == "High":
            recs.append(f"Nitrogen estimated High ({n:.1f} kg/ha): Reduce synthetic N application to avoid vegetative lodging.")
        if status.P == "Low":
            recs.append(f"Phosphorus estimated Low ({p:.1f} kg/ha): Apply basal DAP or SSP near the root zone.")
        elif status.P == "High":
            recs.append(f"Phosphorus estimated High ({p:.1f} kg/ha): Hold phosphate application and monitor Zn availability.")
        if status.K == "Low":
            recs.append(f"Potassium estimated Low ({k:.1f} kg/ha): Supplement with Muriate of Potash (MOP) or compost.")
        elif status.K == "High":
            recs.append(f"Potassium estimated High ({k:.1f} kg/ha): Maintain routine crop residue recycling.")
        if not recs:
            recs.append("Estimated N, P, K balance falls within Optimal agronomic bounds; continue maintenance fertility.")
        recs.append("Confirm vision-based estimates with a certified KVK laboratory soil assay before large-scale dosing.")
        return recs

    @classmethod
    def predict_from_bytes(cls, image_bytes: bytes) -> NPKPredictionResponse:
        if not image_bytes or len(image_bytes) < 512:
            raise ValueError("Image payload is empty or too small.")

        img_tensor, hist_tensor, raw_rgb, width, height = cls._preprocess_bytes(image_bytes)
        quality_metrics = SoilAnalysisService._analyze_quality(raw_rgb, width, height)

        sess = cls._get_session()
        pred = sess.run(
            ["npk_pred"],
            {"image": img_tensor, "color_hist": hist_tensor},
        )[0][0]

        n_val = round(float(max(0.0, pred[0])), 2)
        p_val = round(float(max(0.0, pred[1])), 2)
        k_val = round(float(max(0.0, pred[2])), 2)

        status_map = cls.classify_npk_status(n_val, p_val, k_val)
        recs = cls.build_recommendations(n_val, p_val, k_val, status_map)
        meta = cls._get_metadata()
        model_source = str(meta.get("model_source", "real_dataset"))

        disclaimer = (
            "VISION AI ESTIMATE: Calibrated on real agricultural leaf & soil datasets via Multimodal CNN + "
            "HSV/LAB Color Constancy ONNX model (ICAR Soil Health Card kg/ha thresholds). "
            "Confirm critical fertilizer prescriptions via accredited laboratory assay."
        )

        return NPKPredictionResponse(
            nitrogen=n_val,
            phosphorus=p_val,
            potassium=k_val,
            status=status_map,
            model_source=model_source,
            inference_engine=f"ONNX Runtime ({', '.join(sess.get_providers())})",
            quality_metrics=quality_metrics,
            recommendations=recs,
            scientific_disclaimer=disclaimer,
        )


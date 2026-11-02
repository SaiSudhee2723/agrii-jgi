import io
import logging
from typing import Tuple, Dict, Any, List
import numpy as np

logger = logging.getLogger("geosense.soil")

# Attempt OpenCV import, with graceful fallback to PIL
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning("OpenCV not installed in environment; falling back to PIL image processing.")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from app.schemas.soil import ImageQualityMetrics, SoilColorAnalysis, SoilAnalysisReport

class SoilAnalysisService:
    """
    Module 1: Soil Image Validation and Preprocessing Pipeline.
    
    IMPORTANT SCIENTIFIC REQUIREMENT:
    Ordinary RGB photographs cannot directly measure actual chemical NPK concentrations.
    This service performs rigorous image quality verification (blur, glare, resolution, lighting)
    and extracts observable physical indicators (color hue, estimated texture, surface moisture),
    while transparently disclaiming quantitative chemical NPK values and recommending lab assays.
    """

    @classmethod
    def evaluate_image_bytes(cls, image_bytes: bytes) -> SoilAnalysisReport:
        if not image_bytes or len(image_bytes) < 1024:
            raise ValueError("Image file is empty or corrupted.")

        if len(image_bytes) > 15 * 1024 * 1024:
            raise ValueError("Image file exceeds maximum allowable size (15 MB).")

        # Load image array
        img_rgb, width, height = cls._load_image(image_bytes)

        # 1. Quality evaluation
        quality_metrics = cls._analyze_quality(img_rgb, width, height)

        # 2. Color & texture extraction
        color_analysis = cls._analyze_color_and_texture(img_rgb)

        # 3. Determine overall quality status
        if not quality_metrics.is_acceptable:
            quality_status = "rejected"
        elif quality_metrics.blur_status == "Optimal" and quality_metrics.lighting_status == "Balanced":
            quality_status = "passed"
        else:
            quality_status = "suboptimal"

        # 4. Formulate recommendations
        recommendations = cls._generate_recommendations(quality_status, quality_metrics, color_analysis)

        disclaimer = (
            "SCIENTIFIC NOTICE: Standard consumer RGB mobile cameras capture visible spectrum reflectance "
            "and cannot measure quantitative soil Nitrogen (N), Phosphorus (P), or Potassium (K) chemical "
            "concentrations without laboratory wet-chemistry reagents or calibrated multispectral/NIR spectroscopy. "
            "Geosense reports observable physical attributes (color, estimated texture, moisture condition) and "
            "strongly advises a validated laboratory soil test for precise fertilizer application."
        )

        return SoilAnalysisReport(
            quality_status=quality_status,
            quality_metrics=quality_metrics,
            color_analysis=color_analysis,
            nitrogen_level="Laboratory Test Required (Spectroscopic / Chemical Assay)",
            phosphorus_level="Laboratory Test Required (Bray / Olsen Method)",
            potassium_level="Laboratory Test Required (Ammonium Acetate Extraction)",
            scientific_disclaimer=disclaimer,
            lab_test_recommended=True,
            recommendations=recommendations,
            raw_details={
                "image_width": width,
                "image_height": height,
                "opencv_accelerated": OPENCV_AVAILABLE
            }
        )

    @classmethod
    def _load_image(cls, image_bytes: bytes) -> Tuple[np.ndarray, int, int]:
        if OPENCV_AVAILABLE:
            np_arr = np.frombuffer(image_bytes, np.uint8)
            img_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if img_bgr is None:
                raise ValueError("Could not decode image format. Ensure image is JPG, PNG, or WEBP.")
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            h, w = img_rgb.shape[:2]
            return img_rgb, w, h
        elif PIL_AVAILABLE:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img_rgb = np.array(image)
            w, h = image.size
            return img_rgb, w, h
        else:
            raise RuntimeError("Neither OpenCV nor Pillow is installed to decode images.")

    @classmethod
    def _analyze_quality(cls, img_rgb: np.ndarray, width: int, height: int) -> ImageQualityMetrics:
        # Min resolution check
        is_res_ok = width >= 250 and height >= 250

        # Convert to Grayscale
        if OPENCV_AVAILABLE:
            gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            # Blur score via Laplacian variance
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            blur_score = float(laplacian.var())
        else:
            gray = np.dot(img_rgb[..., :3], [0.2989, 0.5870, 0.1140])
            # Approximation of gradient magnitude for sharpness
            gy, gx = np.gradient(gray)
            gnorm = np.sqrt(gx**2 + gy**2)
            blur_score = float(np.var(gnorm) * 10)

        # Blur classification
        if blur_score > 120.0:
            blur_status = "Optimal"
        elif blur_score > 50.0:
            blur_status = "Moderate Sharpness"
        else:
            blur_status = "Blurry / Out of Focus"

        # Glare / Overexposure check (> 245 luminance)
        glare_mask = (gray > 245)
        glare_ratio = float(np.sum(glare_mask) / gray.size)

        # Underexposure check (< 30 luminance)
        shadow_mask = (gray < 30)
        shadow_ratio = float(np.sum(shadow_mask) / gray.size)

        if glare_ratio > 0.15:
            lighting_status = "Excessive Glare / Overexposed"
        elif shadow_ratio > 0.35:
            lighting_status = "Too Dark / Underexposed"
        elif glare_ratio > 0.05:
            lighting_status = "Slight Glare"
        else:
            lighting_status = "Balanced"

        mean_rgb = [float(round(val, 2)) for val in np.mean(img_rgb, axis=(0, 1))]
        is_acceptable = is_res_ok and blur_score >= 35.0 and glare_ratio <= 0.30

        return ImageQualityMetrics(
            is_acceptable=is_acceptable,
            blur_score=round(blur_score, 2),
            blur_status=blur_status,
            glare_ratio=round(glare_ratio * 100, 2),
            lighting_status=lighting_status,
            width=width,
            height=height,
            mean_rgb=mean_rgb
        )

    @classmethod
    def _analyze_color_and_texture(cls, img_rgb: np.ndarray) -> SoilColorAnalysis:
        mean_rgb = np.mean(img_rgb, axis=(0, 1))
        r, g, b = int(mean_rgb[0]), int(mean_rgb[1]), int(mean_rgb[2])
        hex_color = f"#{r:02x}{g:02x}{b:02x}"

        # Color interpretation based on standard Munsell / Pedology heuristics
        if r < 75 and g < 75 and b < 75:
            color_desc = "Very Dark / High Organic Matter Indication"
            estimated_moisture = "Moderate to High Surface Moisture"
            estimated_texture = "Loam or Silty Clay Loam"
        elif r > 150 and g > 110 and b < 100:
            color_desc = "Reddish-Brown / Iron-Oxide Rich (Laterite / Red Soil)"
            estimated_moisture = "Dry to Moderate"
            estimated_texture = "Sandy Clay Loam"
        elif r > 160 and g > 150 and b > 120:
            color_desc = "Light Pale / Sandy or Calcareous"
            estimated_moisture = "Dry / Rapid Draining"
            estimated_texture = "Sandy / Coarse Loam"
        elif r > 100 and g > 80 and b < 70:
            color_desc = "Dark Brown / Typical Agricultural Topsoil"
            estimated_moisture = "Moderate"
            estimated_texture = "Medium Loam"
        else:
            color_desc = "Medium Brown Mineral Soil"
            estimated_moisture = "Standard"
            estimated_texture = "Loamy"

        return SoilColorAnalysis(
            dominant_color_hex=hex_color,
            color_description=color_desc,
            estimated_soil_texture=estimated_texture,
            estimated_moisture_level=estimated_moisture
        )

    @classmethod
    def _generate_recommendations(
        cls,
        status: str,
        quality: ImageQualityMetrics,
        color: SoilColorAnalysis
    ) -> List[str]:
        recs = []
        if status == "rejected":
            if quality.blur_status == "Blurry / Out of Focus":
                recs.append("Retake photo holding mobile camera 20-30 cm directly above soil surface.")
            if "Glare" in quality.lighting_status:
                recs.append("Avoid direct harsh sunlight glare; capture under diffuse morning or overcast light.")
            if "Dark" in quality.lighting_status:
                recs.append("Increase ambient lighting or enable phone flash.")
            return recs

        recs.append(f"Physical observation indicates {color.color_description.lower()} with {color.estimated_moisture_level.lower()}.")
        recs.append("Perform a standard soil test (NPK + pH + EC) at your local Krishi Vigyan Kendra (KVK) or certified agricultural lab once every 2 years.")
        recs.append("Add well-decomposed organic farmyard manure (FYM) or compost (5 tonnes/acre) to sustain micro-nutrient and carbon balance.")
        recs.append("Maintain crop rotation with leguminous crops (e.g. chickpea, moong) to naturally replenish soil nitrogen.")
        return recs


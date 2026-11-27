"""
Geosense ML NPK Pipeline - Environment & GPU Setup Verification
Verifies PyTorch CUDA availability on Windows (RTX 4060 8GB VRAM), checks core
computer-vision dependencies, and ensures ml_npk/requirements.txt is up to date.
"""

import os
import sys
import importlib

REQUIREMENTS_CONTENT = """--extra-index-url https://download.pytorch.org/whl/cu126
torch==2.14.1+cu126
torchvision==0.29.1+cu126
timm>=1.0.9
albumentations>=1.4.14
opencv-python>=4.10.0
onnx>=1.16.0
onnxruntime>=1.19.0
onnxscript>=0.1.0
pandas>=2.2.0
numpy>=1.26.0
scikit-learn>=1.5.0
pillow>=10.2.0
"""


def write_requirements():
    req_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    with open(req_path, "w", encoding="utf-8") as f:
        f.write(REQUIREMENTS_CONTENT)
    print(f"[OK] Generated/verified requirements file at: {req_path}")


def check_package(pkg_name: str, import_name: str = None) -> bool:
    mod_name = import_name or pkg_name
    try:
        mod = importlib.import_module(mod_name)
        ver = getattr(mod, "__version__", "installed")
        print(f"  [PASS] {pkg_name:<16} -> {ver}")
        return True
    except ImportError as exc:
        print(f"  [MISS] {pkg_name:<16} -> NOT INSTALLED ({exc})")
        return False


def main():
    print("=" * 64)
    print("Geosense NPK Vision Pipeline - Local RTX 4060 Setup Check")
    print("=" * 64)
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version:    {sys.version.split()[0]}")
    print("-" * 64)

    write_requirements()
    print("-" * 64)
    print("Checking required ML / Vision packages:")

    pkgs = [
        ("torch", "torch"),
        ("torchvision", "torchvision"),
        ("timm", "timm"),
        ("albumentations", "albumentations"),
        ("opencv-python", "cv2"),
        ("onnx", "onnx"),
        ("onnxruntime", "onnxruntime"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("scikit-learn", "sklearn"),
        ("pillow", "PIL"),
    ]

    all_ok = True
    for pkg, imp in pkgs:
        if not check_package(pkg, imp):
            all_ok = False

    print("-" * 64)
    try:
        import torch
        cuda_ok = torch.cuda.is_available()
        print(f"torch.cuda.is_available(): {cuda_ok}")
        if cuda_ok:
            device_idx = torch.cuda.current_device()
            props = torch.cuda.get_device_properties(device_idx)
            vram_gb = props.total_memory / (1024 ** 3)
            print(f"GPU Device [{device_idx}]:       {torch.cuda.get_device_name(device_idx)}")
            print(f"CUDA Toolkit Version:  {torch.version.cuda}")
            print(f"VRAM Capacity:         {vram_gb:.2f} GB")
            print(f"Compute Capability:    {props.major}.{props.minor}")
            print(f"Recommended AMP Mode:  torch.amp.autocast('cuda') enabled (Batch Size 32)")
        else:
            print("[WARN] CUDA is NOT active in PyTorch. Install CUDA build via:")
            print("       pip install -r ml_npk/requirements.txt")
    except ImportError:
        print("[WARN] PyTorch not installed yet. Run:")
        print("       pip install -r ml_npk/requirements.txt")

    print("=" * 64)
    if not all_ok:
        print("Status: Missing dependencies detected. Install ml_npk/requirements.txt first.")
        sys.exit(1)
    print("Status: Environment ready for NPK training and ONNX export.")


if __name__ == "__main__":
    main()

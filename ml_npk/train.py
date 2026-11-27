"""
Geosense NPK Vision Training & Export Script (RTX 4060 CUDA + AMP Optimized)
Loads real dataset splits (ml_npk/data/labels.csv & ml_npk/data/val_labels.csv),
applies WeightedRandomSampler for balanced nutrient representation, trains NPKFusionNet
with AdamW, CosineAnnealingLR, torch.cuda.amp.autocast, and batch_size=32,
logs per-nutrient MAE & Low/Optimal/High accuracy each epoch, and exports to:
  - backend/app/models/npk_model.onnx (verified with onnxruntime)
  - backend/app/models/model_metadata.json ({"model_source": "real_dataset", ...})
"""

import os
import sys
import json
import time
import argparse
from collections import Counter
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, WeightedRandomSampler
from sklearn.model_selection import train_test_split

os.environ.setdefault("NO_ALBUMENTATIONS_UPDATE", "1")

# Ensure local imports resolve regardless of working directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from dataset import NPKVisionDataset
from model import NPKFusionNet
from preprocessing import IMG_SIZE, HIST_DIM

# Scale weights so N (~130-470), P (~4-25), and K (~65-320) contribute balanced gradients
LOSS_SCALE = np.array([120.0, 8.0, 90.0], dtype=np.float32)


def _worker_init(_worker_id):
    import cv2
    cv2.setNumThreads(0)


def parse_args():
    parser = argparse.ArgumentParser(description="Train Geosense NPK Vision Model on RTX 4060")
    parser.add_argument(
        "--csv",
        type=str,
        default=os.path.join(SCRIPT_DIR, "data", "labels.csv"),
        help="Path to training labels CSV (columns: image_path, N, P, K)",
    )
    parser.add_argument(
        "--val-csv",
        type=str,
        default=os.path.join(SCRIPT_DIR, "data", "val_labels.csv"),
        help="Path to held-out validation labels CSV (columns: image_path, N, P, K)",
    )
    parser.add_argument(
        "--backbone",
        type=str,
        default="mobilenetv3_large_100",
        choices=["mobilenetv3_large_100", "efficientnet_b0"],
        help="Pretrained timm backbone",
    )
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=8e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--val-split", type=float, default=0.2)
    parser.add_argument("--num-workers", type=int, default=0, help="DataLoader workers (0 safest on Windows)")
    parser.add_argument("--no-pretrained", action="store_true", help="Disable downloading ImageNet weights")
    return parser.parse_args()


def classify_npk_classes(vals: np.ndarray):
    """
    Classifies [N_samples, 3] continuous kg/ha arrays into 0=Low, 1=Optimal, 2=High
    using ICAR Soil Health Card thresholds:
      N: Low < 280, High > 460 | P: Low < 10, High > 30 | K: Low < 120, High > 280
    """
    n_cls = np.where(vals[:, 0] < 280.0, 0, np.where(vals[:, 0] > 460.0, 2, 1))
    p_cls = np.where(vals[:, 1] < 10.0, 0, np.where(vals[:, 1] > 30.0, 2, 1))
    k_cls = np.where(vals[:, 2] < 120.0, 0, np.where(vals[:, 2] > 280.0, 2, 1))
    return n_cls, p_cls, k_cls


def compute_metrics(preds: np.ndarray, targets: np.ndarray):
    abs_err = np.abs(preds - targets)
    mae_n = float(np.mean(abs_err[:, 0]))
    mae_p = float(np.mean(abs_err[:, 1]))
    mae_k = float(np.mean(abs_err[:, 2]))
    mean_mae = (mae_n + mae_p + mae_k) / 3.0
    norm_mae = float(np.mean(abs_err / LOSS_SCALE[None, :]))

    pn, pp, pk = classify_npk_classes(preds)
    tn, tp, tk = classify_npk_classes(targets)
    acc_n = float(np.mean(pn == tn) * 100.0)
    acc_p = float(np.mean(pp == tp) * 100.0)
    acc_k = float(np.mean(pk == tk) * 100.0)
    mean_acc = (acc_n + acc_p + acc_k) / 3.0
    return {
        "mae_n": mae_n,
        "mae_p": mae_p,
        "mae_k": mae_k,
        "mean_mae": mean_mae,
        "norm_mae": norm_mae,
        "acc_n": acc_n,
        "acc_p": acc_p,
        "acc_k": acc_k,
        "mean_acc": mean_acc,
    }


def build_weighted_sampler(train_df: pd.DataFrame) -> WeightedRandomSampler:
    """Balances sampling across source subfolders (FNNPK, Rice LCC, Soil orders)."""
    folder_keys = [os.path.dirname(str(p).replace("\\", "/")) for p in train_df["image_path"]]
    counts = Counter(folder_keys)
    weights = torch.DoubleTensor([1.0 / counts[k] for k in folder_keys])
    return WeightedRandomSampler(weights=weights, num_samples=len(train_df), replacement=True)


def export_onnx_model(model: nn.Module, onnx_path: str):
    import onnx
    import onnxruntime as ort

    os.makedirs(os.path.dirname(onnx_path), exist_ok=True)
    model_cpu = model.to("cpu").eval()

    dummy_img = torch.randn(1, 3, IMG_SIZE, IMG_SIZE, dtype=torch.float32)
    dummy_hist = torch.randn(1, HIST_DIM, dtype=torch.float32)

    torch.onnx.export(
        model_cpu,
        (dummy_img, dummy_hist),
        onnx_path,
        export_params=True,
        opset_version=17,
        do_constant_folding=True,
        input_names=["image", "color_hist"],
        output_names=["npk_pred"],
        dynamic_axes={
            "image": {0: "batch_size"},
            "color_hist": {0: "batch_size"},
            "npk_pred": {0: "batch_size"},
        },
        dynamo=False,
    )

    onnx_model = onnx.load(onnx_path)
    onnx.checker.check_model(onnx_model)

    with torch.no_grad():
        pt_out = model_cpu(dummy_img, dummy_hist).numpy()

    sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
    ort_out = sess.run(
        ["npk_pred"],
        {"image": dummy_img.numpy(), "color_hist": dummy_hist.numpy()},
    )[0]
    max_diff = float(np.max(np.abs(pt_out - ort_out)))
    size_mb = os.path.getsize(onnx_path) / (1024 * 1024)
    print(f"[ONNX] Exported verified model -> {onnx_path} ({size_mb:.2f} MB, max parity diff: {max_diff:.6f})")


def try_export_tflite(model: nn.Module, tflite_path: str):
    try:
        import ai_edge_torch
        model_cpu = model.to("cpu").eval()
        sample_inputs = (
            torch.randn(1, 3, IMG_SIZE, IMG_SIZE, dtype=torch.float32),
            torch.randn(1, HIST_DIM, dtype=torch.float32),
        )
        edge_model = ai_edge_torch.convert(model_cpu, sample_inputs)
        os.makedirs(os.path.dirname(tflite_path), exist_ok=True)
        edge_model.export(tflite_path)
        size_mb = os.path.getsize(tflite_path) / (1024 * 1024)
        print(f"[TFLite] Exported compatible TFLite model -> {tflite_path} ({size_mb:.2f} MB)")
    except ImportError:
        print("[TFLite] Optional 'ai_edge_torch' not installed on Windows; skipped .tflite export (primary serving uses npk_model.onnx).")
    except Exception as exc:
        print(f"[TFLite] Skipped .tflite export ({exc}); ONNX export remains primary.")


def main():
    args = parse_args()

    if not os.path.exists(args.csv):
        raw_dir = os.path.join(SCRIPT_DIR, "raw_datasets")
        if os.path.exists(raw_dir):
            print("[INFO] Generating real dataset CSV splits via prepare_real_dataset.py...")
            from prepare_real_dataset import main as prepare_real_main
            prepare_real_main()
        else:
            print(f"[WARN] Dataset CSV not found at {args.csv}. Generating synthetic fallback dataset...")
            from generate_sample_data import generate_synthetic_dataset
            generate_synthetic_dataset(os.path.dirname(args.csv), num_samples=200)

    data_root = os.path.dirname(os.path.abspath(args.csv))
    if os.path.exists(args.val_csv):
        train_df = pd.read_csv(args.csv)
        val_df = pd.read_csv(args.val_csv)
        overlap = set(train_df["image_path"]) & set(val_df["image_path"])
        if overlap:
            raise RuntimeError(f"Train/Val path leakage detected across {len(overlap)} images!")
        model_source = "real_dataset" if "raw_datasets" in str(train_df["image_path"].iloc[0]) else "custom_csv"
    else:
        full_df = pd.read_csv(args.csv)
        train_df, val_df = train_test_split(full_df, test_size=args.val_split, random_state=42)
        model_source = "real_dataset" if "raw_datasets" in str(full_df["image_path"].iloc[0]) else "synthetic_demo"

    train_ds = NPKVisionDataset(train_df, data_root=data_root, is_train=True)
    val_ds = NPKVisionDataset(val_df, data_root=data_root, is_train=False)

    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")

    sampler = build_weighted_sampler(train_df)
    loader_kwargs = {
        "num_workers": args.num_workers,
        "pin_memory": use_cuda,
        "persistent_workers": False,
        "worker_init_fn": _worker_init if args.num_workers > 0 else None,
    }

    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        sampler=sampler,
        **loader_kwargs,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=args.batch_size,
        shuffle=False,
        **loader_kwargs,
    )

    print("=" * 84)
    print(
        f"Device: {torch.cuda.get_device_name(0) if use_cuda else 'CPU'} | "
        f"Source: {model_source} | Backbone: {args.backbone} | "
        f"Train: {len(train_ds)} | Val: {len(val_ds)} | BS: {args.batch_size} | WeightedRandomSampler: ON"
    )
    print("=" * 84)

    model = NPKFusionNet(
        backbone_name=args.backbone,
        hist_dim=HIST_DIM,
        pretrained=not args.no_pretrained,
    ).to(device)
    model.init_output_bias(train_df[["N", "P", "K"]].mean().values)

    scale_t = torch.tensor(LOSS_SCALE, dtype=torch.float32, device=device).view(1, 3)
    criterion = nn.SmoothL1Loss(beta=0.15)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs, eta_min=1e-6)
    scaler = torch.amp.GradScaler("cuda", enabled=use_cuda)

    ckpt_dir = os.path.join(SCRIPT_DIR, "checkpoints")
    os.makedirs(ckpt_dir, exist_ok=True)
    best_ckpt_path = os.path.join(ckpt_dir, "best_npk_model.pt")

    best_score = float("inf")
    best_metrics = {}
    start_time = time.time()

    for epoch in range(1, args.epochs + 1):
        model.train()
        train_loss = 0.0

        for imgs, hists, targets in train_loader:
            imgs = imgs.to(device, non_blocking=True)
            hists = hists.to(device, non_blocking=True)
            targets = targets.to(device, non_blocking=True)

            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=use_cuda):
                preds = model(imgs, hists)
                loss = criterion(preds / scale_t, targets / scale_t)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            train_loss += float(loss.item()) * imgs.size(0)

        scheduler.step()
        train_loss /= max(1, len(train_ds))

        # Held-out Validation
        model.eval()
        val_loss = 0.0
        all_preds, all_targets = [], []

        with torch.no_grad():
            for imgs, hists, targets in val_loader:
                imgs = imgs.to(device, non_blocking=True)
                hists = hists.to(device, non_blocking=True)
                targets = targets.to(device, non_blocking=True)

                with torch.amp.autocast("cuda", enabled=use_cuda):
                    preds = model(imgs, hists)
                    loss = criterion(preds / scale_t, targets / scale_t)

                val_loss += float(loss.item()) * imgs.size(0)
                all_preds.append(preds.cpu().numpy())
                all_targets.append(targets.cpu().numpy())

        val_loss /= max(1, len(val_ds))
        preds_np = np.concatenate(all_preds, axis=0)
        targets_np = np.concatenate(all_targets, axis=0)
        m = compute_metrics(preds_np, targets_np)

        saved_mark = ""
        if m["norm_mae"] < best_score:
            best_score = m["norm_mae"]
            best_metrics = {
                "best_epoch": epoch,
                "val_loss": round(val_loss, 4),
                "mae_N": round(m["mae_n"], 2),
                "mae_P": round(m["mae_p"], 2),
                "mae_K": round(m["mae_k"], 2),
                "mean_mae": round(m["mean_mae"], 2),
                "cls_acc_N": round(m["acc_n"], 2),
                "cls_acc_P": round(m["acc_p"], 2),
                "cls_acc_K": round(m["acc_k"], 2),
                "mean_cls_acc": round(m["mean_acc"], 2),
            }
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "backbone": args.backbone,
                    "img_size": IMG_SIZE,
                    "hist_dim": HIST_DIM,
                    "metrics": best_metrics,
                },
                best_ckpt_path,
            )
            saved_mark = " *BEST*"

        lr_now = scheduler.get_last_lr()[0]
        print(
            f"Epoch [{epoch:02d}/{args.epochs:02d}] "
            f"TrLoss:{train_loss:6.4f} ValLoss:{val_loss:6.4f} | "
            f"MAE(N/P/K): {m['mae_n']:5.1f}/{m['mae_p']:4.2f}/{m['mae_k']:5.1f} | "
            f"ClsAcc(N/P/K): {m['acc_n']:5.1f}%/{m['acc_p']:5.1f}%/{m['acc_k']:5.1f}% "
            f"(Avg:{m['mean_acc']:5.1f}%) | LR:{lr_now:.1e}{saved_mark}"
        )

    elapsed = time.time() - start_time
    print("-" * 84)
    print(f"Training completed in {elapsed:.1f}s. Best metrics: {best_metrics}")

    # Export best checkpoint to ONNX
    ckpt = torch.load(best_ckpt_path, map_location="cpu", weights_only=True)
    export_model = NPKFusionNet(backbone_name=args.backbone, hist_dim=HIST_DIM, pretrained=False)
    export_model.load_state_dict(ckpt["model_state_dict"])

    models_out_dir = os.path.join(PROJECT_ROOT, "backend", "app", "models")
    onnx_out_path = os.path.join(models_out_dir, "npk_model.onnx")
    export_onnx_model(export_model, onnx_out_path)

    metadata_payload = {
        "model_source": model_source,
        "threshold_standard": "ICAR Soil Health Card (kg/ha)",
        "backbone": args.backbone,
        "img_size": IMG_SIZE,
        "hist_dim": HIST_DIM,
        "outputs": ["N", "P", "K"],
        "units": "kg/ha",
        "train_samples": int(len(train_df)),
        "val_samples": int(len(val_df)),
        "thresholds": {
            "N": {"low_lt": 280.0, "high_gt": 460.0},
            "P": {"low_lt": 10.0, "high_gt": 30.0},
            "K": {"low_lt": 120.0, "high_gt": 280.0},
        },
        "best_metrics": best_metrics,
        "trained_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    meta_path = os.path.join(models_out_dir, "model_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata_payload, f, indent=2)
    print(f"[META] Wrote model metadata -> {meta_path}")

    tflite_out_path = os.path.join(models_out_dir, "npk_model_int8.tflite")
    try_export_tflite(export_model, tflite_out_path)


if __name__ == "__main__":
    main()

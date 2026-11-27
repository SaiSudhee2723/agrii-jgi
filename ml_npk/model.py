"""
Multimodal CNN + HSV/LAB Color Histogram Fusion Regressor for Soil/Leaf NPK Prediction.
Fuses a pretrained timm vision backbone (mobilenetv3_large_100 or efficientnet_b0)
with a 54-dim HSV+LAB histogram branch into a 3-output [N, P, K] regression head.
"""

import torch
import torch.nn as nn
import timm

from preprocessing import HIST_DIM, IMG_SIZE


class NPKFusionNet(nn.Module):
    def __init__(
        self,
        backbone_name: str = "mobilenetv3_large_100",
        hist_dim: int = HIST_DIM,
        pretrained: bool = True,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.backbone_name = backbone_name
        self.backbone = timm.create_model(
            backbone_name,
            pretrained=pretrained,
            num_classes=0,
            global_pool="avg",
        )
        # Measure actual pooled output width dynamically (e.g., mobilenetv3_large_100 outputs 1280 after conv_head)
        was_training = self.backbone.training
        self.backbone.eval()
        with torch.no_grad():
            backbone_dim = int(self.backbone(torch.zeros(1, 3, IMG_SIZE, IMG_SIZE)).shape[1])
        self.backbone.train(was_training)

        # Color chromaticity branch (HSV + LAB normalized histograms)
        self.color_mlp = nn.Sequential(
            nn.Linear(hist_dim, 128),
            nn.LayerNorm(128),
            nn.SiLU(inplace=True),
            nn.Dropout(dropout * 0.5),
            nn.Linear(128, 64),
            nn.LayerNorm(64),
            nn.SiLU(inplace=True),
        )

        fused_dim = backbone_dim + 64
        self.regressor = nn.Sequential(
            nn.Linear(fused_dim, 256),
            nn.LayerNorm(256),
            nn.SiLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(256, 64),
            nn.SiLU(inplace=True),
            nn.Linear(64, 3),  # Outputs: [Nitrogen, Phosphorus, Potassium]
        )

    def init_output_bias(self, target_means):
        """Initializes final linear bias near dataset mean so gradients start active."""
        with torch.no_grad():
            import numpy as np
            means_t = torch.from_numpy(np.array(target_means, dtype=np.float32, copy=True))
            # softplus^-1(y) = log(exp(y) - 1) ~ y for y > 10
            inv = torch.where(means_t > 10.0, means_t, torch.log(torch.expm1(torch.clamp(means_t, min=1e-2))))
            self.regressor[-1].bias.copy_(inv.to(self.regressor[-1].bias.device))

    def forward(self, image: torch.Tensor, color_hist: torch.Tensor) -> torch.Tensor:
        vis_feats = self.backbone(image)
        col_feats = self.color_mlp(color_hist)
        fused = torch.cat([vis_feats, col_feats], dim=1)
        out = self.regressor(fused)
        return torch.nn.functional.softplus(out)  # Smooth, non-negative, never dead-ReLU'd


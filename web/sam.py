import torch
from segment_anything import SamPredictor, sam_model_registry

# DEVICE = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
DEVICE = torch.device("cpu")
MODEL_TYPE = "vit_b"


def get_mask_predictor(checkpoint_path):
    sam = sam_model_registry[MODEL_TYPE](checkpoint=checkpoint_path).to(device=DEVICE)

    return SamPredictor(sam)

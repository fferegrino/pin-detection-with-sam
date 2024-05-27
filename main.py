from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Any
import numpy as np
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
from PIL import Image
import supervision as sv
from uuid import uuid4

import cv2

app = FastAPI()
templates = Jinja2Templates(directory=".")

app.mount("/static", StaticFiles(directory="./static"), name="static")

import torch
# DEVICE = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
DEVICE = torch.device('cpu')
MODEL_TYPE = "vit_b"
CHECKPOINT_PATH='sam_vit_b_01ec64.pth'

sam = sam_model_registry[MODEL_TYPE](checkpoint=CHECKPOINT_PATH).to(device=DEVICE)

mask_predictor = SamPredictor(sam)


class Item(BaseModel):
    x: Any
    y: Any
    width: Any
    height: Any



image_raw = cv2.imread("static/small.jpg")
image_rgb = cv2.cvtColor(image_raw, cv2.COLOR_BGR2RGB)
image_pil = Image.fromarray(image_rgb)



mask_predictor.set_image(image_rgb)

desired_image_width = 1024

ratio = desired_image_width / image_pil.width

resized_image = image_pil.resize((desired_image_width, int(image_pil.height * ratio)))

def turn_pil_image_to_base64(image, format="JPEG"):
    from io import BytesIO
    import base64

    buffered = BytesIO()
    image.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return "data:image/jpeg;base64," + img_str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):

    img_str = turn_pil_image_to_base64(resized_image)

    return templates.TemplateResponse("index.html", {"request": request, "image": img_str, "width": resized_image.width, "height": resized_image.height})

@app.post("/data")
async def receive_data(item: Item):
    print(item)
    box = [item.x, item.y, item.x + item.width, item.y + item.height]
    unratioed_box = np.array([int(i / ratio) for i in box])
    

    masks, scores, logits = mask_predictor.predict(
        box=unratioed_box,
        multimask_output=True
    )

    results = []

    for mask, score in zip(masks, scores.tolist()):
        unique_id = str(uuid4())
        polygons = [poly.tolist() for poly in sv.mask_to_polygons(mask)]
        image = extract_from_mask(image_rgb, mask)
        image.save(f"cutouts/{unique_id}.png")
        results.append({
            "data": turn_pil_image_to_base64(image, format="PNG"),
            "polygons": polygons,
            "score": score,
            "id": unique_id
        })

    return {
        "results": results
    }


def extract_from_mask(image, mask, crop_box=None, margin=10):
    # Create a new array to store the extracted image
    image_rgba = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)

    # Convert the mask to an alpha channel with values in the range [0, 255]
    alpha = (mask * 255).astype(np.uint8)

    # Copy the RGB channels
    for i in range(3):
        image_rgba[:, :, i] = image[:, :, i]

    # Set the alpha channel
    image_rgba[:, :, 3] = alpha

    # Convert to PIL Image
    image_pil = Image.fromarray(image_rgba)

    # If crop_box is not provided, calculate it
    if crop_box is None:
        # Get the bounding box
        bbox = Image.fromarray(alpha).getbbox()

        # Add the margin
        crop_box = (
            max(0, bbox[0] - margin),
            max(0, bbox[1] - margin),
            min(image_pil.width, bbox[2] + margin),
            min(image_pil.height, bbox[3] + margin)
        )

    cropped_image = image_pil.crop(crop_box)

    return cropped_image

import json
import os
from typing import Annotated, Any
from uuid import uuid4

import cv2
import numpy as np
import supervision as sv
from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image
from pydantic import BaseModel

from web.resources import download_resources
from web.sam import get_mask_predictor

app = FastAPI()
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

resources = download_resources()

original_image = cv2.cvtColor(cv2.imread(str(resources["image_path"])), cv2.COLOR_BGR2RGB)

image_to_show = Image.fromarray(original_image)

desired_image_width = 750

ratio = desired_image_width / image_to_show.width

image_to_show = image_to_show.resize((desired_image_width, int(image_to_show.height * ratio)))

mask_predictor = get_mask_predictor(resources["model_path"])
mask_predictor.set_image(original_image)

temp_folder = "/tmp/labeller"
os.makedirs(temp_folder, exist_ok=True)

selected_folder = "selected"


@app.get("/")
@app.post("/")
def get_index(request: Request):
    img = turns_image_to_base64(image_to_show)

    existing_cutouts = []
    for file in os.listdir(selected_folder):
        if file.endswith(".json"):
            with open(f"{selected_folder}/{file}") as f:
                metadata = json.load(f)
                existing_cutouts.append(metadata)

    data = {
        "request": request,
        "image": img,
        "width": image_to_show.width,
        "height": image_to_show.height,
        "existing_cutouts": existing_cutouts,
        "ratio": ratio,
    }
    return templates.TemplateResponse("index.html.jinja", data)


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


@app.post("/cut/")
def post_cut(request: Request, box: BoundingBox):
    box = np.array([box.x1, box.y1, box.x2, box.y2])
    original_box = box / ratio

    masks, _, _ = mask_predictor.predict(box=original_box, multimask_output=True)

    results = []
    for mask in masks:
        uuid = str(uuid4())
        cutout, bbox = extract_from_mask(original_image, mask)
        base64_cutout = turns_image_to_base64(cutout, format="PNG")
        results.append(
            {
                "id": uuid,
                "image": base64_cutout,
            }
        )

        metadata = {
            "uuid": uuid,
            "bbox": {"x1": bbox[0], "y1": bbox[1], "x2": bbox[2], "y2": bbox[3]},
            "original_bbox": {
                "x1": original_box[0],
                "y1": original_box[1],
                "x2": original_box[2],
                "y2": original_box[3],
            },
            "polygons": [poly.tolist() for poly in sv.mask_to_polygons(mask)],
        }

        with open(f"{temp_folder}/{uuid}.png", "wb") as f:
            cutout.save(f, format="PNG")

        with open(f"{temp_folder}/{uuid}.json", "w") as f:
            f.write(json.dumps(metadata))

    return {"results": results}


@app.post("/select_cutout/")
def post_select_cutout(request: Request, id: Annotated[str, Form()], name: Annotated[str, Form()]):
    import shutil

    shutil.move(f"{temp_folder}/{id}.png", f"{selected_folder}/{id}.png")

    with open(f"{temp_folder}/{id}.json") as f:
        metadata = json.load(f)
        metadata["name"] = name

    with open(f"{selected_folder}/{id}.json", "w") as f:
        f.write(json.dumps(metadata))

    return RedirectResponse("/")


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
            min(image_pil.height, bbox[3] + margin),
        )

    cropped_image = image_pil.crop(crop_box)

    return cropped_image, crop_box


def turns_image_to_base64(image, format="JPEG"):
    import base64
    from io import BytesIO

    buffered = BytesIO()
    image.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return "data:image/jpeg;base64," + img_str

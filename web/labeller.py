import json
import os
from typing import Annotated, Any
from uuid import uuid4

import cv2
import numpy as np
from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image
from pydantic import BaseModel
from starlette.responses import FileResponse

from web.masks import extract_from_mask, refine_mask
from web.resources import download_resources
from web.sam import get_mask_predictor
from web.selected import load_selected_cutouts

app = FastAPI()
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

resources = download_resources()

original_image = cv2.cvtColor(cv2.imread(str(resources["image_path"])), cv2.COLOR_BGR2RGB)

og_image = Image.fromarray(original_image)

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

    existing_cutouts = load_selected_cutouts()

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

        refined_mask, refined_polygon = refine_mask(original_image, mask)

        cutout, bbox = extract_from_mask(original_image, refined_mask)

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
            "polygon": refined_polygon,
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


@app.get("/view/")
def get_view(request: Request):
    existing_cutouts = load_selected_cutouts()

    return templates.TemplateResponse(
        "view.html.jinja",
        {
            "request": request,
            "imageWidth": og_image.width,
            "imageHeight": og_image.height,
            "existing_cutouts": existing_cutouts,
            "image": turns_image_to_base64(og_image),
        },
    )


@app.get("/view/download/")
def get_download_view(request: Request):
    existing_cutouts = load_selected_cutouts()

    view_template = templates.get_template("view.html.jinja")
    view_html = view_template.render(
        request=request,
        imageWidth=og_image.width,
        imageHeight=og_image.height,
        existing_cutouts=existing_cutouts,
        image=turns_image_to_base64(og_image),
    )

    with open(f"{temp_folder}/view.html", "w") as f:
        f.write(view_html)

    return FileResponse(f"{temp_folder}/view.html", media_type="text/html", filename="index.html")


def turns_image_to_base64(image, format="JPEG"):
    import base64
    from io import BytesIO

    buffered = BytesIO()
    image.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return "data:image/jpeg;base64," + img_str

from PIL import Image
import numpy as np
import supervision as sv
from shapely import simplify
from shapely.geometry import Polygon
from shapely.ops import unary_union


def refine_mask(image, mask):
    polygons = [Polygon(poly) for poly in sv.mask_to_polygons(mask)]
    single_polygon = unary_union(polygons)

    if single_polygon.geom_type == "Polygon":
        selected_polygon = single_polygon

    elif single_polygon.geom_type == "MultiPolygon":
        selected_polygon = max(single_polygon.geoms, key=lambda x: x.area)

    else:
        raise ValueError(f"Unexpected geometry type: {single_polygon.geom_type}")

    simplified_polygon = simplify(selected_polygon, 1.0)

    selected_polygon = simplified_polygon.buffer(10, join_style=1).buffer(-10.0, join_style=1)
    polygon = []
    for x, y in zip(selected_polygon.exterior.xy[0], selected_polygon.exterior.xy[1]):
        polygon.append(x)
        polygon.append(y)

    new_mask = sv.polygon_to_mask(
        np.array(selected_polygon.exterior.coords, dtype=np.int32),
        (image.shape[1], image.shape[0]),
    )

    return new_mask, polygon


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
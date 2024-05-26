import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
import cv2
from PIL import Image, ImageDraw

IMAGE = 'pins.jpg'


image_raw = cv2.imread(IMAGE)
image_rgb = cv2.cvtColor(image_raw, cv2.COLOR_BGR2RGB)
image_pil = Image.fromarray(image_rgb)

image_width = image_pil.width
image_height = image_pil.height

image_display_width = 500

ratio = image_width / image_display_width

if "points" not in st.session_state:
    st.session_state["points"] = []

def get_ellipse_coords(point: tuple[int, int]) -> tuple[int, int, int, int]:
    center = point
    radius = 10
    return (
        center[0] - radius,
        center[1] - radius,
        center[0] + radius,
        center[1] + radius,
    )

with st.echo("below"):
    with Image.open("pins.jpg") as img:
        draw = ImageDraw.Draw(img)

        # Draw an ellipse at each coordinate in points
        for point in st.session_state["points"]:
            coords = get_ellipse_coords(point)
            draw.ellipse(coords, fill="red")

        value = streamlit_image_coordinates(img, key="pil")

        if value is not None:
            point = value["x"], value["y"]

            if point not in st.session_state["points"]:
                st.session_state["points"].append(point)
                st.experimental_rerun()

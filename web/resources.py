from pathlib import Path
from urllib.request import urlretrieve

resources_dir = Path("resources")


def download_resources():
    if not resources_dir.exists():
        resources_dir.mkdir()

    image_path = resources_dir / "pins.jpg"
    if not image_path.exists():
        image_url = "https://ik.imagekit.io/thatcsharpguy/posts/documenting-my-pin-collection/pins@high.jpg?updatedAt=1717966640257"
        urlretrieve(image_url, image_path)

    model_path = resources_dir / "sam_vit_b_01ec64.pth"
    if not model_path.exists():
        model_url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
        urlretrieve(model_url, model_path)

    return {"image_path": image_path, "model_path": model_path}

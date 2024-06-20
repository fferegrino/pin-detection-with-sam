import json
import os


def load_selected_cutouts():
    selected_folder = "selected"
    existing_cutouts = []
    for file in os.listdir(selected_folder):
        if file.endswith(".json"):
            with open(f"{selected_folder}/{file}") as f:
                metadata = json.load(f)
                existing_cutouts.append(metadata)
    return existing_cutouts

import json
import sys
from pathlib import Path

from label_studio_sdk.converter.imports.yolo import convert_yolo_to_ls

if __name__ == "__main__":
    operation = sys.argv[1]
    datadir = Path(sys.argv[2])

    if operation == "rename":
        images = (datadir / "images").glob("*.JPG")
        labels = (datadir / "labels").glob("*.txt")
        for image in images:
            old_name = image.stem.split("-")[1]
            image.rename(image.parent / f"{old_name}{image.suffix}")
        for label in labels:
            old_name = label.stem.split("-")[1]
            label.rename(label.parent / f"{old_name}{label.suffix}")
    elif operation == "fillup":
        images = (datadir / "images").glob("*.JPG")
        labeldir = datadir / "labels"
        for image in images:
            new_label = labeldir / f"{image.stem}.txt"
            new_label.touch()
    elif operation == "convert":
        dataset = sys.argv[3]
        convert_yolo_to_ls(
            str(datadir),
            str(datadir / "output.json"),
            image_root_url=f"/data/local-files/?d={dataset}/images",
            image_ext=".JPG",
        )
    elif operation == "cloudreference":
        storage = sys.argv[3]
        convert_yolo_to_ls(
            str(datadir),
            str(datadir / "output.json"),
            image_root_url=f"{storage}",
            image_ext=".JPG",
        )
    elif operation == "mergeclasses":
        initial_path = datadir / "output.json"
        merged_path = datadir / "output_merged.json"
        with initial_path.open() as initial:
            tasks = json.loads(initial.read())
            for task in tasks:
                for annotation in task["annotations"][0]["result"]:
                    annotation["value"]["rectanglelabels"] = ["Waste"]
            with merged_path.open("w") as merged:
                merged.write(json.dumps(tasks))

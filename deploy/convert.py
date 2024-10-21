import sys
from label_studio_sdk.converter.imports.yolo import convert_yolo_to_ls
from pathlib import Path
from uuid import uuid4

if __name__ == "__main__":
    operation = sys.argv[1]
    pack = sys.argv[2]

    datadir = Path(".data") / pack

    if operation == "rename":
        images = (datadir / "images").glob("*.JPG")
        labels = (datadir / "labels").glob("*.txt")
        for image in images:
            old_name = image.stem.split("-")[1]
            image.rename(image.parent / f"{old_name}{image.suffix}")
        for label in labels:
            old_name = label.stem.split("-")[1]
            label.rename(label.parent / f"{old_name}{label.suffix}")
    if operation == "fillup":
        images = (datadir / "images").glob("*.JPG")
        labeldir = datadir / "labels"
        for image in images:
            new_label = labeldir / f"{image.stem}.txt"
            new_label.touch()
    elif operation == "convert":
        convert_yolo_to_ls(
        str(datadir),
        str(datadir / "output.json"),
        image_root_url=f"/data/local-files/?d={pack}/images",
        image_ext=".JPG",
    )


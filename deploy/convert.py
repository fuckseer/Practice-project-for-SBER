import sys
from label_studio_sdk.converter.imports.yolo import convert_yolo_to_ls

if __name__ == "__main__":
    convert_yolo_to_ls(
        ".data/" + sys.argv[1],
        ".data/" + sys.argv[2],
        image_root_url=f"/data/local-files/?d={sys.argv[1]}/images",
        image_ext=".JPG",
    )


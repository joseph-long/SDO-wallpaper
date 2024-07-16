import os
import time
import sys
import random
import AppKit
from bs4 import BeautifulSoup
import requests
from pathlib import Path
from PIL import Image
import objc
import logging

log = logging.getLogger(__name__)

BASE_URL = "https://sdo.gsfc.nasa.gov"

DOWNLOADS_PATH = Path.home() / "Downloads" / "current-sdo-images"


def set_wallpaper(image_path: Path, screen: AppKit.NSScreen):
    ws = AppKit.NSWorkspace.sharedWorkspace()
    url = AppKit.NSURL.fileURLWithPath_(image_path.as_posix())
    options = {}
    error = objc.nil

    ws.setDesktopImageURL_forScreen_options_error_(url, screen, options, error)

    if error:
        raise RuntimeError("Error in PyObjC setting desktop image: {error}")


def resize_and_center_image(
    image_path: Path,
    output_path: Path,
    final_width: int,
    final_height: int,
    background_color: tuple[int, int, int],
):
    log.debug(f"Load {image_path}")
    # Load the original image
    original_image = Image.open(image_path)

    # Resize image if it is larger than the final dimensions
    final_size = int(final_width), int(final_height)
    original_image.thumbnail(final_size, Image.Resampling.LANCZOS)

    # Calculate the padding
    original_width, original_height = original_image.size
    padding_left = int((final_width - original_width) // 2)
    padding_top = int((final_height - original_height) // 2)

    # Create new image with background color
    new_image = Image.new("RGB", final_size, background_color)

    # Paste original image onto the center of the new image
    new_image.paste(original_image, (padding_left, padding_top))

    # Save the result
    log.debug(f"Save padded image to {output_path}")
    new_image.save(output_path)
    return output_path


def download(url: str, dest: Path):
    """
    download image and wait for download to finish
    """
    log.debug(f"Retrieving {url}")
    response = requests.get(url, stream=True)
    with open(dest, "wb") as file:
        for chunk in response.iter_content(chunk_size=128):
            file.write(chunk)
    return dest


def main():
    if os.environ.get("DEBUG"):
        logging.basicConfig(level="DEBUG")
    else:
        logging.basicConfig(level="ERROR")

    srcs = [
        "/assets/img/latest/latest_4096_0193.jpg",
        "/assets/img/latest/latest_4096_0193pfss.jpg",
        "/assets/img/latest/latest_4096_0304.jpg",
        "/assets/img/latest/latest_4096_0304pfss.jpg",
        "/assets/img/latest/latest_4096_0171.jpg",
        "/assets/img/latest/latest_4096_0171pfss.jpg",
        "/assets/img/latest/latest_4096_0211.jpg",
        "/assets/img/latest/latest_4096_0211pfss.jpg",
        "/assets/img/latest/latest_4096_0131.jpg",
        "/assets/img/latest/latest_4096_0131pfss.jpg",
        "/assets/img/latest/latest_4096_0335.jpg",
        "/assets/img/latest/latest_4096_0335pfss.jpg",
        "/assets/img/latest/latest_4096_0094.jpg",
        "/assets/img/latest/latest_4096_0094pfss.jpg",
        "/assets/img/latest/latest_4096_1600.jpg",
        "/assets/img/latest/latest_4096_1600pfss.jpg",
        "/assets/img/latest/latest_4096_1700.jpg",
        "/assets/img/latest/latest_4096_1700pfss.jpg",
        "/assets/img/latest/latest_4096_211193171.jpg",
        "/assets/img/latest/latest_4096_HMIB.jpg",
        "/assets/img/latest/latest_4096_HMIBpfss.jpg",
        "/assets/img/latest/latest_4096_HMIBC.jpg",
        "/assets/img/latest/latest_4096_HMIIC.jpg",
        "/assets/img/latest/latest_4096_HMIIF.jpg",
        "/assets/img/latest/latest_4096_HMII.jpg",
        "/assets/img/latest/latest_4096_HMID.jpg",
    ]

    dest = DOWNLOADS_PATH / "padded"
    dest.mkdir(exist_ok=True)
    for existing in dest.glob("*.jpg"):
        log.debug(f"Removing {existing}...")
        existing.unlink()

    screens = AppKit.NSScreen.screens()
    srcs = random.sample(srcs, k=len(screens))
    for screen, src in zip(screens, srcs):
        name = Path(src).name
        dimensions = screen.devicePixelCounts()
        dl_path = download(f"{BASE_URL}/{src}", DOWNLOADS_PATH / name)
        padded_img = resize_and_center_image(
            dl_path,
            dest / f"{int(time.time())}_{name}",
            dimensions.width,
            dimensions.height,
            background_color=(0, 0, 0),
        )
        set_wallpaper(padded_img, screen)
        log.debug(f"{screen.localizedName()} set to {padded_img}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

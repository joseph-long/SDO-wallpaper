import sys
import random
import AppKit
from bs4 import BeautifulSoup
import requests
from pathlib import Path
from PIL import Image
import objc

BASE_URL = "https://sdo.gsfc.nasa.gov"

DOWNLOADS_PATH = Path.home() / "Downloads" / "current-sdo-images"

def set_wallpaper(image_path : Path, screen: AppKit.NSScreen):
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
    background_color: tuple[int, int, int]
):
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
    new_image.save(output_path)
    return output_path


def download(url : str, dest : Path):
    """
    download image and wait for download to finish
    """
    response = requests.get(url, stream=True)
    with open(dest, "wb") as file:
        for chunk in response.iter_content(chunk_size=128):
            file.write(chunk)
    return dest


def main():
    bs = BeautifulSoup(requests.get(BASE_URL + "/data/").text, features="lxml")
    srcs = [
        x.attrs["href"]
        for x in bs.find_all("a", href=lambda x: x and "latest_4096" in x)
    ]

    dest = DOWNLOADS_PATH / "padded"
    dest.mkdir(exist_ok=True)

    screens = AppKit.NSScreen.screens()
    srcs = random.sample(srcs, k=len(screens))
    for screen, src in zip(screens, srcs):
        name = Path(src).name
        dimensions = screen.devicePixelCounts()
        dl_path = download(f"{BASE_URL}/{src}", DOWNLOADS_PATH / name)
        padded_img = resize_and_center_image(
            dl_path,
            dest / name,
            dimensions.width,
            dimensions.height,
            background_color=(0, 0, 0),
        )
        set_wallpaper(padded_img, screen)
        print(f"{screen.localizedName()} set to {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

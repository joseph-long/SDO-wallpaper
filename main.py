import subprocess
import requests
from pathlib import Path

temp_path = Path.home() / "Downloads" / "sdo-osx-wallpaper.jpg"


def change_wallpaper(image_path):
    script = f"""
    tell application "System Events"
        tell current desktop
            set picture to POSIX file "{image_path}"
            set picture rotation to false
        end tell
    end tell
    """
    subprocess.run(["osascript", "-e", script])


def download_latest_image(url=None):
    """
    download image and wait for download to finish
    """
    if url is None:
        url = "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_4096_HMIIC.jpg"
    response = requests.get(url, stream=True)
    with open(temp_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=128):
            file.write(chunk)
    return temp_path


if __name__ == "__main__":

    download_latest_image()
    change_wallpaper(temp_path)

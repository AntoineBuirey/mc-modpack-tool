import os
import argparse

from .progressBar import ProgressBar
from .archive import ModpackArchive


archive_path = r"C:\vm_utils\modpacks\Toine34's Colony-1.0.3-1.0.3.zip"
download_folder = r"C:\vm_utils\test_install"

def download_modpack(archive_path: str, download_folder: str, use_progress_bar: bool = True):
    archive = ModpackArchive(archive_path)
    os.makedirs(download_folder, exist_ok=True)

    if use_progress_bar:
        pb = ProgressBar(total=2, label="Installing modpack", use_percentage=False)
        ProgressBar.hide_cursor()
        try:
            pb.update(0)
            archive.download_mods(destination_path=download_folder, progress_bar=pb)
            pb.update(1)
            archive.copy_overrides(destination_path=download_folder, progress_bar=pb)
            pb.update(1)
        finally:
            ProgressBar.show_cursor()
            pb.clear()
    else:
        archive.download_mods(destination_path=download_folder)
        archive.copy_overrides(destination_path=download_folder)


def main():
    parser = argparse.ArgumentParser(description="Download and install a modpack from a zip archive.")
    parser.add_argument("archive_path", type=str, help="Path to the modpack zip archive.")
    parser.add_argument("download_folder", type=str, help="Destination folder to download the modpack.")
    parser.add_argument("--no-progress", action="store_true", help="Disable the progress bar display.")
    args = parser.parse_args()

    download_modpack(args.archive_path, args.download_folder, use_progress_bar=not args.no_progress)
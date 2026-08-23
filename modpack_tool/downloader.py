import os
import argparse

from . import api
from .progressBar import ProgressBar
from .archive import ModpackArchive


archive_path = r"C:\vm_utils\modpacks\Toine34's Colony-1.0.3-1.0.3.zip"
download_folder = r"C:\vm_utils\test_install"

def download_modpack(archive_source : str|tuple[int, int], download_folder: str, use_progress_bar: bool = True):
    
    if use_progress_bar:
        pb = ProgressBar(total=3, label="Installing modpack", use_percentage=False)
    else:
        pb = None
    
    if isinstance(archive_source, str):
        with open(archive_source, 'rb') as archive_file:
            archive_content = archive_file.read()
    elif isinstance(archive_source, tuple) and len(archive_source) == 2:
        modpack_id, file_id = archive_source
        archive_content = api.download_mod_file_ram(modpack_id, file_id, progress_bar=pb)
    else:
        raise ValueError("archive_source must be either a file path (str) or a tuple of (modpack_id, file_id).")
    
    if pb:
        pb.update(1)
            
    archive = ModpackArchive(archive_content)
    os.makedirs(download_folder, exist_ok=True)

    archive.download_mods(destination_path=download_folder, progress_bar=pb)
    if pb:
        pb.update(1)
        
    archive.copy_overrides(destination_path=download_folder, progress_bar=pb)
    if pb:
        pb.update(1)
        pb.clear()


def main():
    parser = argparse.ArgumentParser(description="Download and install a modpack from a zip archive.")
    parser.add_argument("--archive_path", "-p", type=str, help="Path to the modpack zip archive.", nargs='?')
    
    parser.add_argument("--modpack_id", "-m", type=int, help="Modpack ID to download from CurseForge.", nargs='?')
    parser.add_argument("--file_id", "-f", type=int, help="File ID to download from CurseForge.", nargs='?')
    
    parser.add_argument("download_folder", type=str, help="Destination folder to download the modpack.")
    parser.add_argument("--no-progress", action="store_true", help="Disable the progress bar display.")
    args = parser.parse_args()
    
    if args.archive_path:
        source = args.archive_path
    elif args.modpack_id and args.file_id:
        source = (args.modpack_id, args.file_id)
    else:
        parser.error("You must provide either an archive path or both modpack_id and file_id.")
    
    download_modpack(source, args.download_folder, use_progress_bar=not args.no_progress)
import os
import argparse

from . import api
from .progressBar import ProgressBar
from .archive import ModpackArchive
from .forge import download_forge_installer, patch_eula, execute_forge_installer
from .openjdk import check_java_installed, get_java_version, install_openjdk

archive_path = r"C:\vm_utils\modpacks\Toine34's Colony-1.0.3-1.0.3.zip"
download_folder = r"C:\vm_utils\test_install"

def download_modpack(archive_source : str|tuple[int, int], download_folder: str, use_progress_bar: bool = True):
    
    if use_progress_bar:
        # steps:
        # 1. download or read modpack archive
        # 2. download & install java (if not installed)
        # 3. download forge installer
        # 4. execute forge installer & patch eula
        # 5. download mods
        # 6. copy overrides
        
        pb = ProgressBar(total=6, label="Installing modpack", use_percentage=False)
    else:
        pb = None
    
    # 1. download or read modpack archive
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
    
    # 2. download & install java (if not installed)
    if not check_java_installed():
        required_java_version = get_java_version(archive.manifest.minecraft_version)
        try:
            install_openjdk(required_java_version, progressbar=pb)
        except Exception as e:
            print(f"you must install java {required_java_version} manually.")
            raise RuntimeError(f"Failed to install OpenJDK: {e}")
    
    # 3. download forge installer
    mc_version = archive.manifest.minecraft_version
    forge_version = archive.manifest.modloader.version
    installer_path = download_forge_installer(mc_version, forge_version, download_folder, progress_bar=pb)
    if pb:
        pb.update(1)
    
    # 4. execute forge installer & patch eula
    if not execute_forge_installer(os.path.basename(installer_path), download_folder):
        raise Exception("Failed to execute Forge installer.")
    if not patch_eula(download_folder):
        raise Exception("Failed to patch EULA.")
    if pb:
        pb.update(1)
        
    # 5. download mods
    archive.download_mods(destination_path=download_folder, progress_bar=pb)
    if pb:
        pb.update(1)
        
    # 6. copy overrides
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
    
    try:
        download_modpack(source, args.download_folder, use_progress_bar=not args.no_progress)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
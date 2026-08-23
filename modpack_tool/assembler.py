import os
import zipfile as zf
from typing import Iterable, Any
import argparse
import itertools
import json

from .manifest import ManifestFile
from .modlist import Mod
from .archive import ModpackArchive
from .dataStorage import DataStorage, ModData


def write_modpack_archive(output_path: str,
                          mods : list[tuple[ManifestFile, Mod]],
                          files2copy: Iterable[tuple[str, bytes]],
                          manifest_content: dict[str, Any] = {}
                          ):
    with zf.ZipFile(output_path, 'w', zf.ZIP_DEFLATED) as zip_file:
        # Write manifest.json
        manifest = manifest_content
        manifest['files'] = []
        modlist = "<ul>\n"
        
        for manifest_entry, modlist_entry in mods:
            manifest['files'].append({
                "projectID": manifest_entry.project_id,
                "fileID": manifest_entry.file_id,
                "required": True,
                "isLocked": False
            })
            modlist += f'<li><a href="{modlist_entry.url}">{modlist_entry.name}</a></li>\n'
        
        modlist += "</ul>"
        
        zip_file.writestr('manifest.json', json.dumps(manifest, indent=4))
        zip_file.writestr('modlist.html', modlist)

        # Write overrides
        for relative_path, content in files2copy:
            zip_file.writestr(relative_path, content)

    

def split_modpack_archive(archive_path: str, output_folder: str):
    file_name = os.path.basename(archive_path)
    with open(archive_path, 'rb') as archive_file:
        archive = ModpackArchive(archive_file.read())
    os.makedirs(output_folder, exist_ok=True)
    
    server_path = os.path.join(output_folder, f"server-{file_name}")
    client_path = os.path.join(output_folder, f"client-{file_name}")

    storage = DataStorage()
    
    server_mods = []
    client_mods = []
    
    for file, mod in archive.mods:
        file_info = storage.get_mod(file.project_id, file.file_id)
        if file_info is None:
            response = input(f"Where should {mod.name} be placed? (server/client/both/skip): ").strip().lower()
            match response.lower():
                case 'server':
                    file_info = ModData(file.project_id, file.file_id, True, False)
                case 'client':
                    file_info = ModData(file.project_id, file.file_id, False, True)
                case 'both':
                    file_info = ModData(file.project_id, file.file_id, True, True)
                case 'skip':
                    continue
                case _:
                    print(f"Invalid response. Skipping {mod.name}.")
                    continue
            storage.insert_mod(file_info)
            
        if file_info.server:
            server_mods.append((file, mod))
        if file_info.client:
            client_mods.append((file, mod))
            
    manifest_content_client = archive.manifest.content.copy()
    manifest_content_client['name'] = f"{archive.manifest.name} client"
    write_modpack_archive(
        server_path,
        server_mods,
        itertools.chain(archive.overrides, archive.profileimage),
        manifest_content_client
    )
    
    manifest_content_server = archive.manifest.content.copy()
    manifest_content_server['name'] = f"{archive.manifest.name} server"
    write_modpack_archive(
        client_path,
        client_mods,
        itertools.chain(archive.overrides, archive.profileimage),
        manifest_content_server
    )
    
    
def main():
    parser = argparse.ArgumentParser(description="Split a modpack archive into server and client archives.")
    parser.add_argument("archive_path", type=str, help="Path to the modpack zip archive.")
    parser.add_argument("output_folder", type=str, help="Destination folder to save the split archives.", default=os.getcwd(), nargs='?')
    args = parser.parse_args()

    split_modpack_archive(args.archive_path, args.output_folder)
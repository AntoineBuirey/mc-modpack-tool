import zipfile
import os
from typing import Generator

from . import api
from .manifest import Manifest
from .modlist import ModList
from .progressBar import ProgressBar

class ModpackArchive:
    def __init__(self, file_path : str):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.zip_file = zipfile.ZipFile(file_path, 'r')
        with self.zip_file.open('manifest.json') as manifest_file:
            self.manifest = Manifest(manifest_file)
        with self.zip_file.open('modlist.html') as modlist_file:
            self.modlist = ModList(modlist_file) #type: ignore
        
        if len(self.manifest) != len(self.modlist):
            raise ValueError(f"Mismatch in number of mods: Manifest has {len(self.manifest)} mods, but ModList has {len(self.modlist)} mods.")
    
    def copy_overrides(self, destination_path : str, progress_bar : ProgressBar | None = None):
        files = [file_info for file_info in self.zip_file.infolist() if file_info.filename.startswith('overrides/')]
    
        pb = progress_bar.set_subbar(len(files), "Copying overrides", True) if progress_bar else None
        for file_info in files:
            relative_path = file_info.filename[len('overrides/'):]
            target_path = os.path.join(destination_path, relative_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with self.zip_file.open(file_info) as source_file:
                with open(target_path, 'wb') as target_file:
                    target_file.write(source_file.read())
            pb.update(1) if pb else None
        progress_bar.remove_subbar() if progress_bar else None
    
    @property
    def overrides(self) -> Generator[tuple[str, bytes], None, None]: # path, content
        for file_info in self.zip_file.infolist():
            if file_info.filename.startswith('overrides/'):
                with self.zip_file.open(file_info) as source_file:
                    content = source_file.read()
                yield (file_info.filename, content)
    
    @property
    def profileimage(self) -> Generator[tuple[str, bytes], None, None]: # path, content
        for file_info in self.zip_file.infolist():
            if file_info.filename.startswith('profileimage/'):
                with self.zip_file.open(file_info) as source_file:
                    content = source_file.read()
                yield (file_info.filename, content)
        
    @property
    def mods(self):
        return zip(self.manifest.files, self.modlist.mods)
    
    def __len__(self):
        return len(self.manifest)
    
    def download_mods(self, destination_path : str, progress_bar : ProgressBar | None = None):
        pb = progress_bar.set_subbar(len(self), "Downloading mods", True) if progress_bar else None
        for file, mod in self.mods:
            file_info = api.get_file_info(file.project_id, file.file_id)
            filename = file_info.get('fileName', 'Unknown') if file_info else 'Unknown'
            
            match mod.type:
                case 'mod':
                    target_path = os.path.join(destination_path, 'mods', filename)
                case 'shaders':
                    target_path = os.path.join(destination_path, 'shaderpacks', filename)
                case 'texturepack':
                    target_path = os.path.join(destination_path, 'resourcepacks', filename)
                case _:
                    target_path = os.path.join(destination_path, 'others', filename)
            
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            success = api.download_mod_file(file.project_id, mod.name, file.file_id, target_path, pb)
            pb.update(1) if pb else None
        progress_bar.remove_subbar() if progress_bar else None
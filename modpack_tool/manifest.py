import json
from typing import Generator, IO

from .classes import Version, ManifestFile, ModLoader

class Manifest:
    def __init__(self, stream : IO):
            self.__data : dict = json.load(stream)
        
    @property
    def minecraft_version(self) -> Version:
        str_version = self.__data.get('minecraft', {}).get('version', None)
        if str_version:
            return Version.from_string(str_version)
        else:
            raise ValueError("Minecraft version not found in manifest.")
    
    @property
    def modloader(self) -> ModLoader:
        modloader = self.__data.get('minecraft', {}).get('modLoaders', [])
        if modloader:
            loader_info = modloader[0]
            loader_id = loader_info.get('id', None)
            if loader_id:
                name, version_str = loader_id.split('-', 1)
                return ModLoader(name=name.capitalize(), version=Version.from_string(version_str))
        raise ValueError("Modloader information not found in manifest.")
    
    @property
    def name(self) -> str:
        return self.__data.get('name', "")

    @property
    def version(self) -> str:
        return self.__data.get('version', "")
    
    @property
    def content(self) -> dict:
        result = self.__data.copy()
        result.pop('files', None)
        return result
    
    @property
    def files(self) -> Generator[ManifestFile, None, None]:
        for file in self.__data.get('files', []):
            yield ManifestFile(
                project_id=file.get('projectID', None),
                file_id=file.get('fileID', None),
                required=file.get('required', False),
                isLocked=file.get('isLocked', False)
            )
    
    def __getitem__(self, index: str):
        keys = index.split('.')
        value = self.__data
        for key in keys:
            if isinstance(value, dict):
                if key in value:
                    value = value[key]
                else:
                    raise KeyError(f"Key '{key}' not found in manifest.")
            elif isinstance(value, list):
                try:
                    idx = int(key)
                    value = value[idx]
                except (ValueError, IndexError):
                    raise IndexError(f"Index '{key}' is out of range for the list.")
            else:
                raise TypeError(f"Cannot access key '{key}' in a non-dict/list value.")
        return value
        
            
    def __len__(self):
        return len(self.__data.get('files', []))
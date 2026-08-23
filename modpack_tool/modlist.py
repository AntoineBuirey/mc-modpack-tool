from dataclasses import dataclass
from typing import Generator, Literal, TextIO
import zipfile
import re

RE_NAME = re.compile(r'^(.*) \(by (.*)\)$')
RE_TYPE = re.compile(r'^https://www\.curseforge\.com/minecraft/(mc-mods|shaders|texture-packs)/.*$')

@dataclass
class Mod:
    name: str
    creator: str
    url: str
    type: Literal['mod', 'shaders', 'texturepack', 'unknown']


class ModList:
    def __init__(self, stream : zipfile.ZipExtFile | TextIO):
        # can came from open() or zipfile.open()
        lines = stream.read()
        if isinstance(lines, bytes):
            lines = lines.decode('utf-8')
        
        self.lines = [l for l in lines.splitlines() if l.startswith('<li><a href=')]
    
    @property
    def mods(self) -> Generator[Mod, None, None]:
        for line in self.lines:
            line = line.strip()
            
            url_start = line.find('"') + 1
            url_end = line.find('"', url_start)
            url = line[url_start:url_end]
            
            name_start = line.find('>', url_end) + 1
            name_end = line.find('</a>', name_start)
            name = line[name_start:name_end]
            if match := RE_NAME.match(name):
                mod_name = match.group(1)
                creator = match.group(2)
            else:
                mod_name = name
                creator = "Unknown"
            
            if match := RE_TYPE.match(url):
                mod_type = match.group(1)
                match mod_type:
                    case 'mc-mods':
                        mod_type = 'mod'
                    case 'shaders':
                        mod_type = 'shaders'
                    case 'texture-packs':
                        mod_type = 'texturepack'
                    case _:
                        mod_type = 'unknown'
            else:
                mod_type = 'unknown'
                
            yield Mod(name=mod_name, creator=creator, url=url, type=mod_type)
                
    def __len__(self):
        return len(self.lines)


if __name__ == "__main__":
    with open(r"C:\vm_utils\modpacks\Toine34's Colony Editable - 1.0.3\modlist.html", 'r', encoding="utf-8") as f:
        modlist = ModList(f)
    for mod in modlist.mods:
        print(f"{mod.name}\n\tCreator: {mod.creator}\n\tURL: {mod.url}\n\tType: {mod.type}\n")
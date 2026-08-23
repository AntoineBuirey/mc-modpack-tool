from dataclasses import dataclass
from typing import Literal

@dataclass
class Version:
    major: int
    minor: int
    patch: int
    
    @classmethod
    def from_string(cls, version_str : str):
        parts = version_str.split('.')
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return Version(major, minor, patch)
    
    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def __hash__(self):
        return hash((self.major, self.minor, self.patch))
    
    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
    
    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __gt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)
    
    def __le__(self, other):
        return self < other or self == other
    
    def __ge__(self, other):
        return self > other or self == other

@dataclass
class ManifestFile:
    project_id: int
    file_id: int
    required: bool
    isLocked: bool
    
@dataclass
class ModLoader:
    name: Literal['Fabric', 'Forge', 'Neoforge']
    version: Version
    
@dataclass
class Mod:
    name: str
    creator: str
    url: str
    type: Literal['mod', 'shaders', 'texturepack', 'unknown']

@dataclass
class ModData:
    mod_id: int
    file_id: int
    server: bool
    client: bool
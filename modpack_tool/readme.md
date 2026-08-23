# Minecraft Modpack Tools

## Downloader

download a modpack from curseforge and install it to a specified folder. The modpack can be provided as a zip archive or by specifying the modpack ID and file ID from CurseForge.

### usage:

```bash
modpack-downloader -m <modpack-id> -f <file-id> /path/to/destination/folder
```

## Assembler

split a modpack into two packs: one with client-side mods & content, and another with server-side mods & content. This is useful for creating a server pack and a client pack from a single modpack.

### usage:

```bash
modpack-assembler /path/to/modpack.zip [/path/to/destination/folder]
```

> If the destination folder is not provided, the modpack will be split in the same directory as the original modpack.

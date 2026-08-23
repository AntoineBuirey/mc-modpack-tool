from urllib import request
import os
import subprocess
from pathlib import Path

from .progressBar import ProgressBar
from .classes import Version

def download_forge_installer(mc_version: Version, forge_version: Version, destination_dir: str, progress_bar: ProgressBar | None = None) -> str:
    """
    Downloads the Forge installer for the specified Minecraft version and Forge version.
    """
    download_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{mc_version}-{forge_version}/forge-{mc_version}-{forge_version}-installer.jar"
    destination_path = os.path.join(destination_dir, f"forge-{mc_version}-{forge_version}-installer.jar")
    print(f"Downloading {download_url} to {destination_path}...")
    # Forge's Maven server rejects urllib's default Python-urllib User-Agent.
    download_request = request.Request(
        download_url,
        headers={
            'User-Agent': 'curl/8.0',
            'Accept': '*/*',
        },
    )
    # get the size of the file to be downloaded
    with request.urlopen(download_request) as response:
        if response.status == 200:
            content_length = response.getheader('Content-Length')
            total_size = int(content_length) if content_length else 0
            downloaded_size = 0
            sub_pb = progress_bar.set_subbar(total_size, f"Forge {mc_version}-{forge_version}", True) if progress_bar else None
            with open(destination_path, 'wb') as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if sub_pb:
                        sub_pb.update(len(chunk))
            progress_bar.remove_subbar() if progress_bar else None
            return destination_path
        else:
            raise Exception(f"Failed to download Forge installer. HTTP status code: {response.status}")


def execute_forge_installer(installer_name: str, install_directory: str) -> bool:
    """
    Executes the Forge installer with the specified installation directory.
    """
    log_path = Path("/var/log/modpack-tool/forge_installer.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    with log_path.open("a", encoding="utf-8") as log_file:
        command = ['java', '-jar', installer_name, '--installServer']
        try:
            result = subprocess.run(command, cwd=install_directory, check=True, stdout=log_file, stderr=log_file)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"Error executing command {' '.join(command)}: {e}")
            return False
    
def patch_eula(install_directory: str) -> bool:
    """
    Patches the EULA file to accept the EULA.
    """
    eula_path = os.path.join(install_directory, 'eula.txt')
    try:    
        if os.path.exists(eula_path):
            with open(eula_path, 'r') as f:
                content = f.read()
            content = content.replace('eula=false', 'eula=true')
        else:
            content = 'eula=true\n'
        with open(eula_path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error patching EULA file: {e}")
        return False


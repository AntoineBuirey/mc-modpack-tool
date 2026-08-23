import subprocess
import sys
import os

from .progressBar import ProgressBar
from .classes import Version


def check_java_installed() -> bool:
    try:
        subprocess.run(['java', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error checking Java version: {e}")
        return False
    return True

def get_java_version(minecraft_version: Version) -> int:
    """
    Returns the requied Java version for the given Minecraft version.
    """
    mapping ={
        Version(1,7,0): 8,
        Version(1,17,0) : 16,
        Version(1,18,0) : 17,
        Version(1,20,5) : 21
    }
    for version, java_version in sorted(mapping.items(), reverse=True):
        if minecraft_version >= version:
            return java_version
    raise ValueError(f"No Java version mapping found for Minecraft version {minecraft_version}. Please update the mapping in the code.")
    


def install_openjdk(version: int, progressbar : ProgressBar|None = None) -> None:
    """
    Installe automatiquement une version spécifique d'OpenJDK (Temurin Headless)
    sur Debian 12 (Bookworm) et Debian 13 (Trixie).
    """
    if not sys.platform == "linux":
        raise EnvironmentError("This function is only supported on Linux systems.")
    
    # 1. Vérification des privilèges Root / Sudo
    if os.geteuid() != 0:
        raise PermissionError("This function requires root privileges. Please run the script as root or with sudo.")

    pb = progressbar.set_subbar(5, f"Installing OpenJDK {version}", use_percentage=False) if progressbar else None

    try:
        subprocess.run(["apt-get", "update"], check=True)
        subprocess.run(["apt-get", "install", "-y", "wget", "apt-transport-https", "gnupg"], check=True)
        if pb:
            pb.update(1)

        os.makedirs("/etc/apt/keyrings", exist_ok=True)
        # Téléchargement et installation propre de la clé GPG
        wget_proc = subprocess.Popen(["wget", "-O", "-", "https://adoptium.net"], stdout=subprocess.PIPE)
        with open("/etc/apt/keyrings/adoptium.asc", "wb") as gpg_file:
            subprocess.run(["tee"], stdin=wget_proc.stdout, stdout=gpg_file, check=True)
        wget_proc.wait()
        if pb:
            pb.update(1)

        # Récupère le nom de code de la distribution (ex: bookworm, trixie)
        codename_proc = subprocess.run(["lsb_release", "-cs"], capture_output=True, text=True)
        codename = codename_proc.stdout.strip()
        
        # Alternative si lsb_release n'est pas installé
        if not codename:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("VERSION_CODENAME="):
                        codename = line.split("=")[1].strip().strip('"')

        if not codename:
            raise ValueError("Could not determine the distribution codename. Please ensure lsb_release is installed or check /etc/os-release.")

        repo_line = f"deb [signed-by=/etc/apt/keyrings/adoptium.asc] https://adoptium.net {codename} main\n"
        with open("/etc/apt/sources.list.d/adoptium.list", "w") as repo_file:
            repo_file.write(repo_line)
        if pb:
            pb.update(1)

        subprocess.run(["apt-get", "update"], check=True)
        if pb:
            pb.update(1)

        package_name = f"temurin-{version}-jdk-headless"
        
        # Vérification si le paquet existe dans les dépôts mis à jour
        check_pkg = subprocess.run(["apt-cache", "show", package_name], capture_output=True)
        if check_pkg.returncode != 0:
            raise ValueError(f"Package {package_name} not found in the repositories. Please check the version or the repository configuration.")

        subprocess.run(["apt-get", "install", "-y", package_name], check=True)
        if pb:
            pb.update(1)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred while executing a command: {e}")
    except Exception as e:
        raise RuntimeError(f"An error occurred during the installation of OpenJDK {version}: {e}")
    
    if progressbar:
        progressbar.remove_subbar()
